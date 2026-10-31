import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.assessment import Assessment
from app.schemas.assessment import (
    AssessmentStartRequest,
    AssessmentStartResponse,
    AssessmentSubmitRequest,
    AssessmentSubmitResponse,
    ConceptScoreDetail
)
from app.services.subject_service import subject_service
from app.services.learner_service import learner_service

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.post("/start", response_model=AssessmentStartResponse)
def start_assessment(payload: AssessmentStartRequest, db: Session = Depends(get_db)):
    """Initialize a diagnostic or practice assessment."""
    learner = learner_service.get_learner_by_id(db, payload.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found.")

    subject = subject_service.get_subject(payload.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{payload.subject_id}' not found.")

    assessment_id = str(uuid.uuid4())
    assessment = Assessment(
        id=assessment_id,
        learner_id=learner.id,
        subject_id=subject.id,
        assessment_type=payload.assessment_type or "diagnostic",
        total_questions=len(subject.diagnostic)
    )
    db.add(assessment)
    db.commit()

    return AssessmentStartResponse(
        assessment_id=assessment_id,
        learner_id=learner.id,
        subject_id=subject.id,
        assessment_type=assessment.assessment_type,
        questions=subject.diagnostic
    )

@router.post("/{assessment_id}/submit", response_model=AssessmentSubmitResponse)
def submit_assessment(
    assessment_id: str,
    payload: AssessmentSubmitRequest,
    db: Session = Depends(get_db)
):
    """Submit all answers for an assessment, grade, and update concept masteries."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    subject = subject_service.get_subject(assessment.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found.")

    questions = subject.diagnostic
    if len(payload.answers) != len(questions):
        raise HTTPException(
            status_code=400,
            detail=f"Expected {len(questions)} answers, received {len(payload.answers)}."
        )

    correct_count = 0
    concept_results = []
    
    # Existing records before update
    existing_records = learner_service.get_concept_records_for_learner(
        db, assessment.learner_id, assessment.subject_id
    )

    for i, q in enumerate(questions):
        student_ans = payload.answers[i]
        is_correct = (student_ans == q.answer)
        if is_correct:
            correct_count += 1

        old_mastery = existing_records.get(q.conceptId).mastery if q.conceptId in existing_records else 0

        updated_mastery = learner_service.update_mastery_record(
            db=db,
            learner_id=assessment.learner_id,
            subject_id=assessment.subject_id,
            concept_id=q.conceptId,
            is_correct=is_correct,
            question_prompt=q.prompt,
            selected_answer=student_ans
        )

        concept_results.append(
            ConceptScoreDetail(
                concept_id=q.conceptId,
                is_correct=is_correct,
                old_mastery=old_mastery,
                new_mastery=updated_mastery.mastery_score
            )
        )

    score_pct = round((correct_count / len(questions)) * 100, 1)
    assessment.score = score_pct
    assessment.answers_json = json.dumps(payload.answers)
    assessment.completed_at = datetime.utcnow()
    db.commit()

    return AssessmentSubmitResponse(
        assessment_id=assessment_id,
        learner_id=assessment.learner_id,
        subject_id=assessment.subject_id,
        score_percentage=score_pct,
        correct_count=correct_count,
        total_questions=len(questions),
        concept_results=concept_results,
        message=f"Assessment completed: {correct_count}/{len(questions)} correct ({score_pct}%)."
    )
