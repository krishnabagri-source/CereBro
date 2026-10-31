from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.subject import SubjectSummary, SubjectDetail, ConceptSchema
from app.services.subject_service import subject_service

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.get("", response_model=List[SubjectSummary])
def get_subjects():
    """Retrieve all available subjects across all domains."""
    return subject_service.list_subjects()

@router.get("/{subject_id}", response_model=SubjectDetail)
def get_subject_detail(subject_id: str):
    """Retrieve complete subject details, concepts, and diagnostics."""
    subject = subject_service.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{subject_id}' not found.")
    return subject

@router.get("/{subject_id}/concepts", response_model=List[ConceptSchema])
def get_subject_concepts(subject_id: str):
    """Retrieve all concepts for a specific subject."""
    subject = subject_service.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{subject_id}' not found.")
    return subject.concepts
