from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    learner_id = Column(Integer, ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(50), nullable=False)
    assessment_type = Column(String(50), default="diagnostic")
    score = Column(Float, default=0.0)
    total_questions = Column(Integer, default=0)
    answers_json = Column(Text, default="[]")
    completed_at = Column(DateTime, default=datetime.utcnow)

    learner = relationship("Learner", back_populates="assessments")
