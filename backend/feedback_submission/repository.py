from sqlalchemy.ext.asyncio import AsyncSession

from models.feedback_submission import FeedbackSubmission


async def create_feedback_submission(
    db: AsyncSession,
    feedback_submission: FeedbackSubmission
) -> FeedbackSubmission:

    db.add(feedback_submission)

    await db.commit()
    await db.refresh(feedback_submission)

    return feedback_submission
