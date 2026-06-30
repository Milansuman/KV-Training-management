from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.feedback_submission import FeedbackSubmission
from feedback_submission import repository


async def create_feedback_submission(
    db: AsyncSession,
    user_id: int,
    recipient_id: Optional[int],
    feedback_id: int,
    text: str
) -> FeedbackSubmission:

    submission = FeedbackSubmission(
        user_id=user_id,
        recipient_id=recipient_id,
        feedback_id=feedback_id,
        text=text
    )

    return await repository.create_feedback_submission(
        db=db,
        feedback_submission=submission
    )
