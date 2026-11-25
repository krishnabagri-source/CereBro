from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.learner import LearnerCreate, LearnerResponse, LearnerProgressResponse
from app.services.learner_service import learner_service
from app.services.subject_service import subject_service
from app.services.adaptive_engine import adaptive_engine

router = APIRouter(prefix="/learners", tags=["Learners"])

@router.post("", response_model=LearnerResponse, status_code=201)
def create_learner(payload: LearnerCreate, db: Session = Depends(get_db)):
    """Create a new learner profile."""
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Learner name cannot be empty.")
    subject_id = payload.subject_id or "algebra"
    learner = learner_service.create_learner(db, name, subject_id=subject_id)
    return learner_service.get_learner_response(db, learner)

@router.get("", response_model=List[LearnerResponse])
def list_learners(db: Session = Depends(get_db)):
    """List all learners in the database."""
    learners = learner_service.get_all_learners(db)
    return [learner_service.get_learner_response(db, l) for l in learners]

@router.get("/{learner_id}", response_model=LearnerResponse)
def get_learner(learner_id: int, db: Session = Depends(get_db)):
    """Get single learner details with concept mastery records."""
    learner = learner_service.get_learner_by_id(db, learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found.")
    return learner_service.get_learner_response(db, learner)

@router.get("/{learner_id}/progress", response_model=LearnerProgressResponse)
def get_learner_progress(
    learner_id: int,
    subject_id: Optional[str] = Query(None, description="Optional subject ID filter"),
    db: Session = Depends(get_db)
):
    """Retrieve detailed learning progress, mastery metrics, and gap analysis."""
    learner = learner_service.get_learner_by_id(db, learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found.")

    target_subject_id = subject_id or learner.active_subject_id
    subject = subject_service.get_subject(target_subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{target_subject_id}' not found.")

    records = learner_service.get_concept_records_for_learner(db, learner.id, target_subject_id)
    
    total_concepts = len(subject.concepts)
    concepts_mastered = 0
    total_mastery_sum = 0
    total_attempts = 0
    weak_concepts = []
    strong_concepts = []

    for concept in subject.concepts:
        r = records.get(concept.id)
        if r:
            total_mastery_sum += r.mastery
            total_attempts += r.attempts
            if r.mastery >= adaptive_engine.MASTERY_COMPLETED_THRESHOLD:
                concepts_mastered += 1
                strong_concepts.append(concept.id)
            elif r.attempts > 0 and r.mastery < adaptive_engine.MASTERY_PREREQUISITE_THRESHOLD:
                weak_concepts.append(concept.id)

    overall_mastery = round(total_mastery_sum / total_concepts) if total_concepts > 0 else 0

    return LearnerProgressResponse(
        learner_id=learner.id,
        name=learner.name,
        subject_id=target_subject_id,
        overall_mastery=overall_mastery,
        concepts_mastered=concepts_mastered,
        total_concepts=total_concepts,
        total_attempts=total_attempts,
        concepts=records,
        weak_concepts=weak_concepts,
        strong_concepts=strong_concepts
    )
