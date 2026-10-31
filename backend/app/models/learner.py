from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Learner(Base):
    __tablename__ = "learners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    active_subject_id = Column(String(50), default="algebra")
    activity_log = Column(Text, default="[]")  # JSON encoded list of strings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    mastery_records = relationship("ConceptMastery", back_populates="learner", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="learner", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="learner", cascade="all, delete-orphan")
