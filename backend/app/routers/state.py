from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.subject_service import subject_service
from app.services.learner_service import learner_service

router = APIRouter(tags=["Frontend Compatibility State"])

def get_public_state(db: Session, active_idx: int = 0, subject_id: str = "algebra") -> Dict[str, Any]:
    learners = learner_service.get_all_learners(db)
    if not learners:
        learner_service.ensure_seed_learners(db)
        learners = learner_service.get_all_learners(db)

    active_idx = max(0, min(len(learners) - 1, active_idx))
    active_learner = learners[active_idx]
    
    current_subject = subject_id or active_learner.active_subject_id or "algebra"

    formatted_learners = []
    for l in learners:
        resp = learner_service.get_learner_response(db, l)
        formatted_learners.append({
            "id": l.id,
            "name": l.name,
            "records": {k: v.model_dump() for k, v in resp.records.items()},
            "activity": resp.activity
        })

    return {
        "learners": formatted_learners,
        "active": active_idx,
        "subject": current_subject,
        "subjects": [s.model_dump() for s in subject_service.list_subjects()]
    }

@router.get("/health")
def health_check():
    return {"ok": True, "name": "AdaptIQ / CereBro Universal Backend", "version": "1.0.0"}

@router.get("/state")
def get_state(db: Session = Depends(get_db)):
    """State endpoint powering the existing frontend."""
    return get_public_state(db, active_idx=0, subject_id="algebra")

@router.put("/selection")
def update_selection(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Update active demo learner or selected subject."""
    active = int(payload.get("active", 0))
    subject = str(payload.get("subject", "algebra"))

    learners = learner_service.get_all_learners(db)
    if 0 <= active < len(learners):
        learners[active].active_subject_id = subject
        db.commit()

    return get_public_state(db, active_idx=active, subject_id=subject)

@router.post("/diagnostic")
def submit_diagnostic(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Evaluate diagnostic quiz and update learner mastery across tested concepts."""
    active = int(payload.get("active", 0))
    subject_id = str(payload.get("subjectId", "algebra"))
    answers = payload.get("answers", [])

    learners = learner_service.get_all_learners(db)
    if not (0 <= active < len(learners)):
        raise HTTPException(status_code=400, detail="Invalid learner index.")

    learner = learners[active]
    subject = subject_service.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=400, detail="Invalid subject ID.")

    if not isinstance(answers, list) or len(answers) != len(subject.diagnostic):
        raise HTTPException(status_code=400, detail="Diagnostic answers are incomplete.")

    for i, item in enumerate(subject.diagnostic):
        is_corr = (answers[i] == item.answer)
        learner_service.update_mastery_record(
            db=db,
            learner_id=learner.id,
            subject_id=subject_id,
            concept_id=item.conceptId,
            is_correct=is_corr,
            question_prompt=item.prompt,
            selected_answer=answers[i]
        )

    learner.active_subject_id = subject_id
    db.commit()

    return get_public_state(db, active_idx=active, subject_id=subject_id)

@router.post("/practice")
def submit_practice(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Evaluate practice answer, update mastery, and return updated state."""
    active = int(payload.get("active", 0))
    subject_id = str(payload.get("subjectId", "algebra"))
    concept_id = str(payload.get("conceptId", ""))
    answer = int(payload.get("answer", -1))

    learners = learner_service.get_all_learners(db)
    if not (0 <= active < len(learners)):
        raise HTTPException(status_code=400, detail="Invalid learner index.")

    learner = learners[active]
    subject = subject_service.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=400, detail="Invalid subject.")

    concept = subject_service.get_concept(subject_id, concept_id)
    if not concept:
        raise HTTPException(status_code=400, detail="Invalid concept.")

    if not (0 <= answer < len(concept.practice.choices)):
        raise HTTPException(status_code=400, detail="Invalid answer choice index.")

    is_correct = (answer == concept.practice.answer)
    updated_mastery = learner_service.update_mastery_record(
        db=db,
        learner_id=learner.id,
        subject_id=subject_id,
        concept_id=concept_id,
        is_correct=is_correct,
        question_prompt=concept.practice.prompt,
        selected_answer=answer
    )

    learner.active_subject_id = subject_id
    db.commit()

    state = get_public_state(db, active_idx=active, subject_id=subject_id)
    all_records = learner_service.get_concept_records_for_learner(db, learner.id, subject_id)
    
    return {
        **state,
        "correct": is_correct,
        "record": all_records[concept_id].model_dump()
    }
