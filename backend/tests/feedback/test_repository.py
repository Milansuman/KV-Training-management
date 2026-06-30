import pytest

from feedback import repository
from models.feedback import Feedback, FeedbackType
from models.feedback_submission import FeedbackSubmission


async def _seed_feedback(db_session, session_id: int) -> Feedback:
    feedback = Feedback(session_id=session_id, type=FeedbackType.TEXT)
    db_session.add(feedback)
    await db_session.commit()
    await db_session.refresh(feedback)
    return feedback


async def _seed_submission(db_session, feedback_id: int, user_id: int = 1, text: str = "test") -> FeedbackSubmission:
    submission = FeedbackSubmission(user_id=user_id, feedback_id=feedback_id, text=text)
    db_session.add(submission)
    await db_session.commit()
    await db_session.refresh(submission)
    return submission


@pytest.mark.asyncio
async def test_get_submissions_by_session_id_returns_matching(db_session) -> None:
    feedback = await _seed_feedback(db_session, session_id=10)
    await _seed_submission(db_session, feedback_id=feedback.id, text="First submission.")
    await _seed_submission(db_session, feedback_id=feedback.id, text="Second submission.")

    results = await repository.get_submissions_by_session_id(db=db_session, session_id=10)

    assert len(results) == 2
    texts = {r.text for r in results}
    assert texts == {"First submission.", "Second submission."}


@pytest.mark.asyncio
async def test_get_submissions_by_session_id_returns_empty_for_no_match(db_session) -> None:
    results = await repository.get_submissions_by_session_id(db=db_session, session_id=999)

    assert results == []


@pytest.mark.asyncio
async def test_get_submissions_by_session_id_does_not_return_other_sessions(db_session) -> None:
    feedback_a = await _seed_feedback(db_session, session_id=20)
    feedback_b = await _seed_feedback(db_session, session_id=21)

    await _seed_submission(db_session, feedback_id=feedback_a.id, text="Session 20.")
    await _seed_submission(db_session, feedback_id=feedback_b.id, text="Session 21.")

    results = await repository.get_submissions_by_session_id(db=db_session, session_id=20)

    assert len(results) == 1
    assert results[0].text == "Session 20."


@pytest.mark.asyncio
async def test_get_submissions_by_session_id_excludes_soft_deleted(db_session) -> None:
    from datetime import datetime, UTC

    feedback = await _seed_feedback(db_session, session_id=30)
    alive = await _seed_submission(db_session, feedback_id=feedback.id, text="Alive.")
    deleted = await _seed_submission(db_session, feedback_id=feedback.id, text="Deleted.")

    deleted.deleted_at = datetime.now(tz=UTC)
    await db_session.commit()

    results = await repository.get_submissions_by_session_id(db=db_session, session_id=30)

    assert len(results) == 1
    assert results[0].text == "Alive."


@pytest.mark.asyncio
async def test_get_submissions_by_session_id_multiple_feedbacks_same_session(db_session) -> None:
    # A session can have multiple feedback records; all their submissions should be returned.
    feedback_1 = await _seed_feedback(db_session, session_id=40)
    feedback_2 = await _seed_feedback(db_session, session_id=40)

    await _seed_submission(db_session, feedback_id=feedback_1.id, text="From feedback 1.")
    await _seed_submission(db_session, feedback_id=feedback_2.id, text="From feedback 2.")

    results = await repository.get_submissions_by_session_id(db=db_session, session_id=40)

    assert len(results) == 2
