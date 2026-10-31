from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learner_id = Column(Integer, ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(50), nullable=False, index=True)
    concept_id = Column(String(50), nullable=False, index=True)
    mastery_score = Column(Integer, default=0)  # 0 to 100
    attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    difficulty = Column(Integer, default=1)  # 1 = Beginner, 2 = Intermediate, 3 = Advanced
    consecutive_correct = Column(Integer, default=0)
    last_practiced = Column(DateTime, nullable=True)
    due_at = Column(DateTime, nullable=True)
    history_json = Column(Text, default="[]")  # JSON encoded list of ISO timestamps

    learner = relationship("Learner", back_populates="mastery_records")

    __table_args__ = (
        UniqueConstraint("learner_id", "subject_id", "concept_id", name="uq_learner_subject_concept"),
    )
