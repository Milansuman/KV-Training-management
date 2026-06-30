from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schema import TokenPayload
from db.connection import get_db
from auth.dependencies import get_current_user

from feedback import service
from feedback_submission.schemas import FeedbackSubmissionResponse


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


@router.get(
    "/session/{session_id}",
    response_model=list[FeedbackSubmissionResponse]
)
async def get_submissions_by_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    return await service.get_submissions_by_session_id(
        db=db,
        session_id=session_id
    )
