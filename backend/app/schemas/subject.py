from typing import List, Optional
from pydantic import BaseModel, Field

class QuestionSchema(BaseModel):
    prompt: str
    choices: List[str]
    answer: int
    explanation: str
    hints: Optional[List[str]] = Field(default_factory=list)
    difficulty: Optional[int] = 1

class DiagnosticQuestionSchema(QuestionSchema):
    conceptId: str

class MisconceptionSchema(BaseModel):
    misconception: str
    explanation: str

class ConceptSchema(BaseModel):
    id: str
    title: str
    description: str
    level: str
    learning_objectives: Optional[List[str]] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    difficulty_level: Optional[int] = 1
    lesson: str
    example: str
    practice: QuestionSchema
    question_bank: Optional[List[QuestionSchema]] = Field(default_factory=list)
    common_misconceptions: Optional[List[MisconceptionSchema]] = Field(default_factory=list)

class SubjectSummary(BaseModel):
    id: str
    name: str
    domain: str
    level: str
    description: str
    icon: str
    color: str
    concepts_count: int

class SubjectDetail(BaseModel):
    id: str
    name: str
    domain: str
    level: str
    description: str
    icon: str
    color: str
    concepts: List[ConceptSchema]
    diagnostic: List[DiagnosticQuestionSchema]
