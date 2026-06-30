from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schema import TokenPayload
from db.connection import get_db
from auth.dependencies import get_current_user

from feedback_submission import service
from feedback_submission.schemas import FeedbackSubmissionCreateRequest, FeedbackSubmissionResponse


router = APIRouter(
    prefix="/feedback-submissions",
    tags=["Feedback Submissions"]
)


@router.post(
    "",
    response_model=FeedbackSubmissionResponse
)
async def create_feedback_submission(
    payload: FeedbackSubmissionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    return await service.create_feedback_submission(
        db=db,
        user_id=payload.user_id,
        recipient_id=payload.recipient_id,
        feedback_id=payload.feedback_id,
        text=payload.text
    )
