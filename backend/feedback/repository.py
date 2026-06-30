from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.feedback import Feedback
from models.feedback_submission import FeedbackSubmission


async def get_submissions_by_session_id(
    db: AsyncSession,
    session_id: int
) -> list[FeedbackSubmission]:

    result = await db.scalars(
        select(FeedbackSubmission)
        .join(Feedback, FeedbackSubmission.feedback_id == Feedback.id)
        .where(Feedback.session_id == session_id)
        .where(FeedbackSubmission.deleted_at.is_(None))
    )

    return list(result.all())
