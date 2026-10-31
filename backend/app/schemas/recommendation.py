from typing import List, Optional
from pydantic import BaseModel
from app.schemas.subject import ConceptSchema
from app.schemas.learner import ConceptRecordState

class RecommendationResponse(BaseModel):
    learner_id: int
    subject_id: str
    recommended_concept: Optional[ConceptSchema] = None
    reason: str
    priority_level: str  # high, normal, review
    weak_concepts: List[str]
    mastered_concepts: List[str]

class RoadmapItemResponse(BaseModel):
    concept: ConceptSchema
    record: ConceptRecordState
    status: str  # completed, in-progress, ready, locked
    prerequisites_met: bool
    missing_prerequisites: List[str]

class RoadmapResponse(BaseModel):
    learner_id: int
    subject_id: str
    steps: List[RoadmapItemResponse]

class RevisionItemResponse(BaseModel):
    concept_id: str
    concept_title: str
    mastery: int
    attempts: int
    due_at: str
    is_due_now: bool
    status: str

class RevisionsResponse(BaseModel):
    learner_id: int
    subject_id: str
    due_now: List[RevisionItemResponse]
    upcoming: List[RevisionItemResponse]
    total_due: int
