from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ConceptRecordState(BaseModel):
    mastery: int = Field(default=0, ge=0, le=100)
    attempts: int = 0
    correct: int = 0
    accuracy: float = 0.0
    difficulty: int = 1
    lastPracticed: Optional[str] = None
    dueAt: Optional[str] = None
    history: List[str] = Field(default_factory=list)

class LearnerCreate(BaseModel):
    name: str
    subject_id: Optional[str] = "algebra"

class LearnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    active_subject_id: str
    records: Dict[str, ConceptRecordState] = Field(default_factory=dict)
    activity: List[str] = Field(default_factory=list)

class LearnerProgressResponse(BaseModel):
    learner_id: int
    name: str
    subject_id: str
    overall_mastery: int
    concepts_mastered: int
    total_concepts: int
    total_attempts: int
    concepts: Dict[str, ConceptRecordState]
    weak_concepts: List[str]
    strong_concepts: List[str]
