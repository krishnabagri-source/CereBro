import pytest
from fastapi import HTTPException
from app.routers.subjects import get_subjects, get_subject_detail, get_subject_concepts

def test_get_subjects():
    subjects = get_subjects()
    assert len(subjects) >= 3
    ids = [s.id for s in subjects]
    assert "algebra" in ids
    assert "python" in ids
    assert "security" in ids
    assert "physics" in ids  # Universal domain support!

def test_get_subject_detail():
    data = get_subject_detail("algebra")
    assert data.id == "algebra"
    assert data.domain == "Mathematics"
    assert len(data.concepts) == 3
    assert len(data.diagnostic) == 3

def test_get_subject_concepts():
    concepts = get_subject_concepts("python")
    assert len(concepts) == 3
    concept_ids = [c.id for c in concepts]
    assert "variables" in concept_ids
    assert "conditionals" in concept_ids
    assert "loops" in concept_ids

def test_subject_not_found():
    with pytest.raises(HTTPException) as exc_info:
        get_subject_detail("non_existent_subject_123")
    assert exc_info.value.status_code == 404
