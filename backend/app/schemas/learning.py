from typing import List, Optional
from pydantic import BaseModel
from app.schemas.learner import ConceptRecordState

class AskQuestionRequest(BaseModel):
    learner_id: int
    subject_id: str
    concept_id: str
    query: str
    action: Optional[str] = "doubt"  # doubt, explain, hint, practice

class AskQuestionResponse(BaseModel):
    subject_id: str
    concept_id: str
    response: str
    action: str
    hints: Optional[List[str]] = None
    is_ai_generated: bool = False

class SubmitAnswerRequest(BaseModel):
    learner_id: int
    subject_id: str
    concept_id: str
    answer_index: int
    reasoning: Optional[str] = None

class SubmitAnswerResponse(BaseModel):
    learner_id: int
    subject_id: str
    concept_id: str
    is_correct: bool
    correct_answer: int
    explanation: str
    old_mastery: int
    new_mastery: int
    due_at: str
    record: ConceptRecordState
    detected_misconception: Optional[str] = None
    ai_feedback: Optional[str] = None
