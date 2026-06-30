import pytest

from feedback import service
from models.feedback import Feedback, FeedbackType
from models.feedback_submission import FeedbackSubmission


async def _seed_feedback(db_session, session_id: int) -> Feedback:
    feedback = Feedback(session_id=session_id, type=FeedbackType.TEXT)
    db_session.add(feedback)
    await db_session.commit()
    await db_session.refresh(feedback)
    return feedback


async def _seed_submission(db_session, feedback_id: int, text: str = "test") -> FeedbackSubmission:
    submission = FeedbackSubmission(user_id=1, feedback_id=feedback_id, text=text)
    db_session.add(submission)
    await db_session.commit()
    await db_session.refresh(submission)
    return submission


@pytest.mark.asyncio
async def test_get_submissions_by_session_id_returns_list(db_session) -> None:
    feedback = await _seed_feedback(db_session, session_id=50)
    await _seed_submission(db_session, feedback_id=feedback.id, text="Service test.")

    results = await service.get_submissions_by_session_id(db=db_session, session_id=50)

    assert len(results) == 1
    assert results[0].text == "Service test."


@pytest.mark.asyncio
async def test_get_submissions_by_session_id_returns_empty_list(db_session) -> None:
    results = await service.get_submissions_by_session_id(db=db_session, session_id=999)

    assert results == []


@pytest.mark.asyncio
async def test_get_submissions_by_session_id_only_returns_correct_session(db_session) -> None:
    feedback_target = await _seed_feedback(db_session, session_id=60)
    feedback_other = await _seed_feedback(db_session, session_id=61)

    await _seed_submission(db_session, feedback_id=feedback_target.id, text="Target session.")
    await _seed_submission(db_session, feedback_id=feedback_other.id, text="Other session.")

    results = await service.get_submissions_by_session_id(db=db_session, session_id=60)

    assert len(results) == 1
    assert results[0].text == "Target session."
