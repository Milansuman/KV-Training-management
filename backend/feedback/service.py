from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.feedback import Feedback, FeedbackType
from models.feedback_submission import FeedbackSubmission
from feedback import repository
from sqlalchemy.exc import NoResultFound

from exceptions.exceptions import NotFoundException

async def create_feedback(
    db: AsyncSession,
    session_id: int,
    type: FeedbackType = FeedbackType.TEXT,
    url: Optional[str] = None
) -> Feedback:

    feedback = Feedback(
        session_id=session_id,
        type=type,
        url=url
    )

    return await repository.create_feedback(
        db=db,
        feedback=feedback
    )


async def get_feedback_by_session_id(
    db: AsyncSession,
    session_id: int
) -> Feedback | None:

    return await repository.get_feedback_by_session_id(
        db=db,
        session_id=session_id
    )


async def get_submissions_by_session_id(
    db: AsyncSession,
    session_id: int
) -> list[FeedbackSubmission]:

    submission = await repository.get_submissions_by_session_id(
        db=db,
        session_id=session_id
    )
    if submission is None or submission == []:
        raise NotFoundException(
            "No feedback submissions found for this session"
        )
    return submission

async def delete_feedback_by_session_id(
    db: AsyncSession,
    session_id: int
):
    feedback = await get_feedback_by_session_id(
        db=db,
        session_id=session_id
    )

    if feedback is None:
        raise NotFoundException(
            "Feedback not found"
        )

    await repository.delete_feedback(
        db=db,
        feedback=feedback
    )