from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recommendation import RecommendationResponse, RoadmapResponse
from app.services.subject_service import subject_service
from app.services.learner_service import learner_service
from app.services.adaptive_engine import adaptive_engine

router = APIRouter(tags=["Recommendations & Roadmap"])

@router.get("/learners/{learner_id}/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    learner_id: int,
    subject_id: Optional[str] = Query(None, description="Optional subject ID"),
    db: Session = Depends(get_db)
):
    """
    Get personalized adaptive concept recommendation.
    Different learners receive distinct recommendations based on strengths and gaps.
    """
    learner = learner_service.get_learner_by_id(db, learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found.")

    target_subject_id = subject_id or learner.active_subject_id
    subject = subject_service.get_subject(target_subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{target_subject_id}' not found.")

    records = learner_service.get_concept_records_for_learner(db, learner.id, target_subject_id)
    return adaptive_engine.get_recommendation(subject, records, learner.id)

@router.get("/learners/{learner_id}/roadmap", response_model=RoadmapResponse)
def get_roadmap(
    learner_id: int,
    subject_id: Optional[str] = Query(None, description="Optional subject ID"),
    db: Session = Depends(get_db)
):
    """
    Get prerequisite-aware roadmap showing concept states (locked, ready, in-progress, completed).
    """
    learner = learner_service.get_learner_by_id(db, learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found.")

    target_subject_id = subject_id or learner.active_subject_id
    subject = subject_service.get_subject(target_subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{target_subject_id}' not found.")

    records = learner_service.get_concept_records_for_learner(db, learner.id, target_subject_id)
    steps = adaptive_engine.generate_roadmap(subject, records)

    return RoadmapResponse(
        learner_id=learner.id,
        subject_id=target_subject_id,
        steps=steps
    )
