import pytest
from datetime import datetime, timedelta
from app.services.adaptive_engine import adaptive_engine
from app.schemas.subject import ConceptSchema, QuestionSchema
from app.schemas.learner import ConceptRecordState

def test_single_correct_answer_not_100_percent():
    """Verify requirement: A single correct answer must NOT result in 100% mastery."""
    new_mastery = adaptive_engine.calculate_mastery_update(
        old_mastery=0,
        is_correct=True,
        current_attempts=0
    )
    assert new_mastery < 100
    assert new_mastery == 50

def test_incorrect_first_answer_gives_low_mastery():
    new_mastery = adaptive_engine.calculate_mastery_update(
        old_mastery=0,
        is_correct=False,
        current_attempts=0
    )
    assert new_mastery <= 15
    assert new_mastery == 10

def test_step_capping_limits_wild_jumps():
    """Verify maximum change per answer is capped at 18 points."""
    # From 50, answering correct: ema is 50*0.7 + 30 = 65, delta is +15
    m1 = adaptive_engine.calculate_mastery_update(old_mastery=50, is_correct=True, current_attempts=1)
    assert abs(m1 - 50) <= 18

    # From 100, answering incorrect: ema is 70, delta is -30 -> capped to -18 -> 82
    m2 = adaptive_engine.calculate_mastery_update(old_mastery=100, is_correct=False, current_attempts=5)
    assert m2 == 82
    assert (100 - m2) == 18

def test_prerequisites_check():
    concept = ConceptSchema(
        id="linear",
        title="Linear",
        description="test",
        level="Beginner",
        prerequisites=["expressions"],
        lesson="test",
        example="test",
        practice=QuestionSchema(prompt="q", choices=["a"], answer=0, explanation="e")
    )
    
    # Locked when prerequisite is below 60%
    records_locked = {"expressions": ConceptRecordState(mastery=55)}
    ready, missing = adaptive_engine.check_prerequisites(concept, records_locked)
    assert ready is False
    assert "expressions" in missing

    # Unlocked when prerequisite is at or above 60%
    records_ready = {"expressions": ConceptRecordState(mastery=65)}
    ready, missing = adaptive_engine.check_prerequisites(concept, records_ready)
    assert ready is True
    assert len(missing) == 0

def test_spaced_repetition_scheduling():
    now = datetime.utcnow()
    
    # Incorrect -> due tomorrow
    due_bad = adaptive_engine.calculate_revision_date(is_correct=False, new_mastery=20)
    assert (due_bad - now).days == 1

    # Correct low mastery -> due in 2 days
    due_low = adaptive_engine.calculate_revision_date(is_correct=True, new_mastery=55)
    assert (due_low - now).days == 2

    # Correct high mastery -> due in 7 days
    due_high = adaptive_engine.calculate_revision_date(is_correct=True, new_mastery=90)
    assert (due_high - now).days == 7

def test_difficulty_adaptation():
    # Consecutive correct increases difficulty
    diff, consec = adaptive_engine.adjust_difficulty(current_difficulty=1, is_correct=True, consecutive_correct=1)
    assert diff == 2
    assert consec == 0

    # Incorrect drops difficulty and resets consecutive
    diff2, consec2 = adaptive_engine.adjust_difficulty(current_difficulty=2, is_correct=False, consecutive_correct=1)
    assert diff2 == 1
    assert consec2 == 0
