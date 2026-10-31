from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.learning import (
    AskQuestionRequest,
    AskQuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse
)
from app.schemas.learner import ConceptRecordState
from app.services.subject_service import subject_service
from app.services.learner_service import learner_service
from app.services.adaptive_engine import adaptive_engine
from app.services.ai_tutor import ai_tutor

router = APIRouter(prefix="/learning", tags=["Learning & AI Tutor"])

@router.post("/ask", response_model=AskQuestionResponse)
def ask_ai_tutor(payload: AskQuestionRequest, db: Session = Depends(get_db)):
    """
    Communicate with the AI Teaching Assistant:
    - action='explain': Explains concept at learner's current mastery level with real-world examples.
    - action='hint': Provides pedagogical progressive hint for practice without giving away answer.
    - action='practice': Generates or selects an adaptive question for current difficulty.
    - action='doubt': Answers general questions and doubts regarding the concept.
    """
    learner = learner_service.get_learner_by_id(db, payload.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found.")

    subject = subject_service.get_subject(payload.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{payload.subject_id}' not found.")

    concept = subject_service.get_concept(payload.subject_id, payload.concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept '{payload.concept_id}' not found.")

    records = learner_service.get_concept_records_for_learner(db, learner.id, subject.id)
    record = records.get(concept.id, ConceptRecordState())

    action = payload.action or "doubt"

    if action == "explain":
        result = ai_tutor.explain_concept(
            subject_name=subject.name,
            concept=concept,
            learner_mastery=record.mastery,
            difficulty_level=record.difficulty
        )
        return AskQuestionResponse(
            subject_id=subject.id,
            concept_id=concept.id,
            response=result["text"],
            action="explain",
            is_ai_generated=result["is_ai_generated"]
        )

    elif action == "hint":
        result = ai_tutor.provide_hint(
            subject_name=subject.name,
            concept=concept,
            question=concept.practice,
            attempt_number=record.attempts + 1
        )
        return AskQuestionResponse(
            subject_id=subject.id,
            concept_id=concept.id,
            response=result["hint"],
            action="hint",
            hints=concept.practice.hints,
            is_ai_generated=result["is_ai_generated"]
        )

    elif action == "practice":
        result = ai_tutor.generate_practice_question(
            subject_name=subject.name,
            concept=concept,
            difficulty=record.difficulty
        )
        import json
        return AskQuestionResponse(
            subject_id=subject.id,
            concept_id=concept.id,
            response=json.dumps(result["question"]),
            action="practice",
            is_ai_generated=result["is_ai_generated"]
        )

    else:  # doubt
        result = ai_tutor.answer_student_doubt(
            subject_name=subject.name,
            concept=concept,
            query=payload.query,
            learner_mastery=record.mastery
        )
        return AskQuestionResponse(
            subject_id=subject.id,
            concept_id=concept.id,
            response=result["answer"],
            action="doubt",
            is_ai_generated=result["is_ai_generated"]
        )

@router.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(payload: SubmitAnswerRequest, db: Session = Depends(get_db)):
    """
    Submits a practice answer:
    - Evaluates correctness.
    - Diagnoses possible misconceptions.
    - Updates learner mastery using the explainable adaptive engine.
    - Schedules spaced revision.
    """
    learner = learner_service.get_learner_by_id(db, payload.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found.")

    subject = subject_service.get_subject(payload.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{payload.subject_id}' not found.")

    concept = subject_service.get_concept(payload.subject_id, payload.concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept '{payload.concept_id}' not found.")

    question = concept.practice
    if payload.answer_index < 0 or payload.answer_index >= len(question.choices):
        raise HTTPException(status_code=400, detail="Invalid answer choice index.")

    is_correct = (payload.answer_index == question.answer)

    # Detect misconception if incorrect
    detected_misconception = None
    ai_feedback = None
    if not is_correct:
        detected_misconception = adaptive_engine.detect_misconception(
            concept=concept,
            selected_index=payload.answer_index,
            student_reasoning=payload.reasoning
        )
        ai_res = ai_tutor.analyze_incorrect_answer(
            subject_name=subject.name,
            concept=concept,
            question=question,
            chosen_index=payload.answer_index,
            student_reasoning=payload.reasoning
        )
        ai_feedback = ai_res.get("feedback")

    # Get old mastery
    records_before = learner_service.get_concept_records_for_learner(db, learner.id, subject.id)
    old_mastery = records_before.get(concept.id).mastery if concept.id in records_before else 0

    # Update mastery via adaptive engine
    updated_mastery = learner_service.update_mastery_record(
        db=db,
        learner_id=learner.id,
        subject_id=subject.id,
        concept_id=concept.id,
        is_correct=is_correct,
        question_prompt=question.prompt,
        selected_answer=payload.answer_index,
        misconception=detected_misconception
    )

    records_after = learner_service.get_concept_records_for_learner(db, learner.id, subject.id)
    updated_record = records_after[concept.id]

    return SubmitAnswerResponse(
        learner_id=learner.id,
        subject_id=subject.id,
        concept_id=concept.id,
        is_correct=is_correct,
        correct_answer=question.answer,
        explanation=question.explanation,
        old_mastery=old_mastery,
        new_mastery=updated_mastery.mastery_score,
        due_at=updated_mastery.due_at.isoformat() if updated_mastery.due_at else "",
        record=updated_record,
        detected_misconception=detected_misconception,
        ai_feedback=ai_feedback
    )
