import pytest
from app.database import Base, engine, SessionLocal
from app.services.learner_service import learner_service
from app.services.subject_service import subject_service

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    learner_service.ensure_seed_learners(db)
    subject_service.load_all_subjects()
    db.close()
    yield

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
