from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.feedback import Feedback
from models.feedback_submission import FeedbackSubmission


async def create_feedback(
    db: AsyncSession,
    feedback: Feedback
) -> Feedback:
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback


async def get_feedback_by_session_id(
    db: AsyncSession,
    session_id: int
) -> Feedback | None:
    result = await db.scalars(
        select(Feedback)
        .where(Feedback.session_id == session_id)
        .where(Feedback.deleted_at.is_(None))
    )
    return result.first()


async def get_submissions_by_session_id(
    db: AsyncSession,
    session_id: int
) -> list[FeedbackSubmission]:

    result = await db.scalars(
        select(FeedbackSubmission)
        .join(Feedback, FeedbackSubmission.feedback_id == Feedback.id)
        .where(Feedback.session_id == session_id)
        .where(Feedback.deleted_at.is_(None))
        .where(FeedbackSubmission.deleted_at.is_(None))
    )

    return list(result.all())

async def delete_feedback(
    db: AsyncSession,
    feedback: Feedback
) -> None:

    feedback.deleted_at = datetime.now(tz=UTC)

    await db.commit()
    await db.refresh(feedback)
