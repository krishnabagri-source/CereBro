import pytest
from app.routers.assessments import start_assessment, submit_assessment
from app.routers.learning import ask_ai_tutor, submit_answer
from app.routers.learners import list_learners
from app.schemas.assessment import AssessmentStartRequest, AssessmentSubmitRequest
from app.schemas.learning import AskQuestionRequest, SubmitAnswerRequest

def test_start_and_submit_diagnostic_assessment(db_session):
    learners = list_learners(db_session)
    learner = learners[0]

    # 1. Start assessment
    start_req = AssessmentStartRequest(
        learner_id=learner.id,
        subject_id="python",
        assessment_type="diagnostic"
    )
    start_res = start_assessment(start_req, db_session)
    assessment_id = start_res.assessment_id
    assert len(start_res.questions) == 3

    # 2. Submit assessment with answers: [1, 1, 1] (all correct for python diagnostic)
    submit_req = AssessmentSubmitRequest(answers=[1, 1, 1])
    submit_res = submit_assessment(assessment_id, submit_req, db_session)
    assert submit_res.score_percentage == 100.0
    assert submit_res.correct_count == 3
    assert len(submit_res.concept_results) == 3

def test_submit_practice_answer_and_misconception(db_session):
    learners = list_learners(db_session)
    learner = learners[0]

    # Submit an incorrect answer to Python variables (choice 0 = 'int' instead of 2 = 'float')
    submit_req = SubmitAnswerRequest(
        learner_id=learner.id,
        subject_id="python",
        concept_id="variables",
        answer_index=0,
        reasoning="I thought all numbers without words are integers"
    )
    data = submit_answer(submit_req, db_session)
    assert data.is_correct is False
    assert data.correct_answer == 2
    assert data.detected_misconception is not None
    assert data.ai_feedback is not None
    assert data.new_mastery <= data.old_mastery

def test_ai_tutor_ask_fallback_safe(db_session):
    learners = list_learners(db_session)
    learner = learners[0]

    # Ask for explanation
    req = AskQuestionRequest(
        learner_id=learner.id,
        subject_id="algebra",
        concept_id="expressions",
        query="Can you explain this simply?",
        action="explain"
    )
    res = ask_ai_tutor(req, db_session)
    assert len(res.response) > 0

    # Ask for hint
    req_hint = AskQuestionRequest(
        learner_id=learner.id,
        subject_id="algebra",
        concept_id="expressions",
        query="",
        action="hint"
    )
    res_hint = ask_ai_tutor(req_hint, db_session)
    assert len(res_hint.response) > 0
