import pytest
from app.routers.state import (
    health_check,
    get_state,
    update_selection,
    submit_diagnostic,
    submit_practice
)

def test_health():
    res = health_check()
    assert res["ok"] is True

def test_state_endpoint_structure(db_session):
    data = get_state(db_session)
    assert "learners" in data
    assert "active" in data
    assert "subject" in data
    assert len(data["learners"]) >= 2
    assert "records" in data["learners"][0]
    assert "activity" in data["learners"][0]

def test_selection_update(db_session):
    data = update_selection({"active": 1, "subject": "python"}, db_session)
    assert data["active"] == 1
    assert data["subject"] == "python"

def test_legacy_diagnostic_submit(db_session):
    data = submit_diagnostic({
        "active": 0,
        "subjectId": "algebra",
        "answers": [0, 1, 1]
    }, db_session)
    assert data["active"] == 0
    assert data["subject"] == "algebra"
    alex = data["learners"][0]
    assert "expressions" in alex["records"]

def test_legacy_practice_submit(db_session):
    data = submit_practice({
        "active": 0,
        "subjectId": "algebra",
        "conceptId": "expressions",
        "answer": 0
    }, db_session)
    assert data["correct"] is True
    assert "record" in data
    assert data["record"]["mastery"] > 0
