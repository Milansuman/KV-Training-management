from sqlalchemy.ext.asyncio import AsyncSession

from models.feedback_submission import FeedbackSubmission
from feedback import repository


async def get_submissions_by_session_id(
    db: AsyncSession,
    session_id: int
) -> list[FeedbackSubmission]:

    return await repository.get_submissions_by_session_id(
        db=db,
        session_id=session_id
    )
