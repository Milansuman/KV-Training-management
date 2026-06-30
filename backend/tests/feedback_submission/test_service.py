import pytest

from feedback_submission import service


@pytest.mark.asyncio
async def test_create_feedback_submission_returns_submission(db_session) -> None:
    created = await service.create_feedback_submission(
        db=db_session,
        user_id=1,
        recipient_id=2,
        feedback_id=1,
        text="Well structured session.",
    )

    assert created.id is not None
    assert created.user_id == 1
    assert created.recipient_id == 2
    assert created.feedback_id == 1
    assert created.text == "Well structured session."


@pytest.mark.asyncio
async def test_create_feedback_submission_without_recipient(db_session) -> None:
    created = await service.create_feedback_submission(
        db=db_session,
        user_id=5,
        recipient_id=None,
        feedback_id=2,
        text="No recipient feedback.",
    )

    assert created.id is not None
    assert created.recipient_id is None


@pytest.mark.asyncio
async def test_create_feedback_submission_sets_submitted_at(db_session) -> None:
    created = await service.create_feedback_submission(
        db=db_session,
        user_id=6,
        recipient_id=None,
        feedback_id=3,
        text="Check timestamp.",
    )

    assert created.submitted_at is not None


@pytest.mark.asyncio
async def test_create_feedback_submission_persists_text(db_session) -> None:
    text = "Detailed feedback about the training content."

    created = await service.create_feedback_submission(
        db=db_session,
        user_id=7,
        recipient_id=8,
        feedback_id=4,
        text=text,
    )

    assert created.text == text
