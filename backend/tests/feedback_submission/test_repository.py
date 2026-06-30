import pytest

from feedback_submission import repository
from models.feedback_submission import FeedbackSubmission


@pytest.mark.asyncio
async def test_create_feedback_submission_returns_submission(db_session) -> None:
    submission = FeedbackSubmission(
        user_id=1,
        recipient_id=2,
        feedback_id=1,
        text="Great session!",
    )

    created = await repository.create_feedback_submission(
        db=db_session,
        feedback_submission=submission,
    )

    assert created.id is not None
    assert created.user_id == 1
    assert created.recipient_id == 2
    assert created.feedback_id == 1
    assert created.text == "Great session!"


@pytest.mark.asyncio
async def test_create_feedback_submission_without_recipient(db_session) -> None:
    submission = FeedbackSubmission(
        user_id=3,
        recipient_id=None,
        feedback_id=2,
        text="Anonymous feedback.",
    )

    created = await repository.create_feedback_submission(
        db=db_session,
        feedback_submission=submission,
    )

    assert created.id is not None
    assert created.recipient_id is None
    assert created.user_id == 3


@pytest.mark.asyncio
async def test_create_feedback_submission_sets_submitted_at(db_session) -> None:
    submission = FeedbackSubmission(
        user_id=4,
        feedback_id=3,
        text="Timestamped.",
    )

    created = await repository.create_feedback_submission(
        db=db_session,
        feedback_submission=submission,
    )

    assert created.submitted_at is not None


@pytest.mark.asyncio
async def test_create_multiple_submissions_get_unique_ids(db_session) -> None:
    sub1 = FeedbackSubmission(user_id=1, feedback_id=1, text="First.")
    sub2 = FeedbackSubmission(user_id=2, feedback_id=1, text="Second.")

    created1 = await repository.create_feedback_submission(db=db_session, feedback_submission=sub1)
    created2 = await repository.create_feedback_submission(db=db_session, feedback_submission=sub2)

    assert created1.id != created2.id
