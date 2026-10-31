from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recommendation import RevisionsResponse, RevisionItemResponse
from app.services.subject_service import subject_service
from app.services.learner_service import learner_service

router = APIRouter(tags=["Revisions"])

@router.get("/learners/{learner_id}/revisions", response_model=RevisionsResponse)
def get_revisions(
    learner_id: int,
    subject_id: Optional[str] = Query(None, description="Optional subject ID"),
    db: Session = Depends(get_db)
):
    """
    Get scheduled spaced-repetition revisions, separated into 'due now' and 'upcoming'.
    """
    learner = learner_service.get_learner_by_id(db, learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found.")

    target_subject_id = subject_id or learner.active_subject_id
    subject = subject_service.get_subject(target_subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{target_subject_id}' not found.")

    records = learner_service.get_concept_records_for_learner(db, learner.id, target_subject_id)
    now = datetime.utcnow()

    due_now = []
    upcoming = []

    for concept in subject.concepts:
        r = records.get(concept.id)
        if not r or not r.dueAt:
            continue

        try:
            due_dt = datetime.fromisoformat(r.dueAt)
        except Exception:
            continue

        is_due = (due_dt <= now)
        item = RevisionItemResponse(
            concept_id=concept.id,
            concept_title=concept.title,
            mastery=r.mastery,
            attempts=r.attempts,
            due_at=r.dueAt,
            is_due_now=is_due,
            status="Due for review" if is_due else "Scheduled"
        )

        if is_due:
            due_now.append(item)
        else:
            upcoming.append(item)

    return RevisionsResponse(
        learner_id=learner.id,
        subject_id=target_subject_id,
        due_now=due_now,
        upcoming=upcoming,
        total_due=len(due_now)
    )
