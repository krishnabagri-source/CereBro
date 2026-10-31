from typing import List, Optional
from pydantic import BaseModel
from app.schemas.subject import DiagnosticQuestionSchema

class AssessmentStartRequest(BaseModel):
    learner_id: int
    subject_id: str
    assessment_type: Optional[str] = "diagnostic"

class AssessmentStartResponse(BaseModel):
    assessment_id: str
    learner_id: int
    subject_id: str
    assessment_type: str
    questions: List[DiagnosticQuestionSchema]

class AssessmentSubmitRequest(BaseModel):
    answers: List[int]

class ConceptScoreDetail(BaseModel):
    concept_id: str
    is_correct: bool
    old_mastery: int
    new_mastery: int

class AssessmentSubmitResponse(BaseModel):
    assessment_id: str
    learner_id: int
    subject_id: str
    score_percentage: float
    correct_count: int
    total_questions: int
    concept_results: List[ConceptScoreDetail]
    message: str
