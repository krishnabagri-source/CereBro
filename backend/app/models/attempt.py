from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learner_id = Column(Integer, ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(50), nullable=False)
    concept_id = Column(String(50), nullable=False)
    question_prompt = Column(Text, nullable=False)
    selected_answer = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    difficulty = Column(Integer, default=1)
    misconception_detected = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    learner = relationship("Learner", back_populates="attempts")
