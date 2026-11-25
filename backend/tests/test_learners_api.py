import pytest
from app.routers.learners import list_learners, get_learner, get_learner_progress, create_learner
from app.routers.recommendations import get_recommendations, get_roadmap
from app.schemas.learner import LearnerCreate

def test_list_learners(db_session):
    learners = list_learners(db_session)
    assert len(learners) >= 2
    names = [l.name for l in learners]
    assert "Alex Morgan" in names
    assert "Sam Rivera" in names

def test_different_learners_receive_different_recommendations(db_session):
    """
    Verify requirement: Two students studying the same subject receive
    different learning paths/recommendations if their mastery profiles differ.
    """
    learners = list_learners(db_session)
    alex = next(l for l in learners if l.name == "Alex Morgan")
    sam = next(l for l in learners if l.name == "Sam Rivera")

    rec_alex = get_recommendations(alex.id, "algebra", db_session)
    rec_sam = get_recommendations(sam.id, "algebra", db_session)

    assert rec_alex.recommended_concept is not None
    assert rec_sam.recommended_concept is not None

    # Alex and Sam have different mastery profiles and receive different recommendations
    assert rec_alex.recommended_concept.id != rec_sam.recommended_concept.id
    assert rec_alex.recommended_concept.id in ("linear", "graphs")
    assert rec_sam.recommended_concept.id == "expressions"

def test_roadmap_prerequisites_status(db_session):
    learners = list_learners(db_session)
    alex = next(l for l in learners if l.name == "Alex Morgan")
    
    roadmap = get_roadmap(alex.id, "algebra", db_session)
    steps = roadmap.steps
    assert len(steps) == 3
    # Step 0 (expressions): Alex has 88% -> completed
    assert steps[0].status == "completed"
    # Step 1 (linear): attempts > 0 -> in-progress or completed depending on practice
    assert steps[1].status in ("in-progress", "completed")

def test_learner_progress(db_session):
    learners = list_learners(db_session)
    alex = next(l for l in learners if l.name == "Alex Morgan")

    progress = get_learner_progress(alex.id, "algebra", db_session)
    assert progress.learner_id == alex.id
    assert progress.total_concepts == 3
    assert progress.concepts_mastered >= 1
    assert "expressions" in progress.strong_concepts

def test_create_new_learner(db_session):
    new_l = create_learner(LearnerCreate(name="Jordan Lee"), db_session)
    assert new_l.name == "Jordan Lee"
    assert new_l.id > 0
