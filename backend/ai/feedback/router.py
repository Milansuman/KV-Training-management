from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from db.connection import get_db

from .graph import agent

router = APIRouter(prefix="/ai/feedback", tags=["Feedback Agent"])

# Map the agent's error codes to HTTP status codes
_ERROR_CODES: dict[str, int] = {
    "not_found": 404,
    "no_feedback": 404,
    "internal_error": 500,
}


class FeedbackSummaryRequest(BaseModel):
    user_id: int
    session_id: int


class FeedbackSummaryResponse(BaseModel):
    user_id: int
    session_id: int
    summaries: dict  # e.g. {"trainer": "...", "moderator": "..."}


@router.post("/summarize", response_model=FeedbackSummaryResponse)
async def summarize_feedback(
    payload: FeedbackSummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> FeedbackSummaryResponse:
    initial_state = {
        "user_id": payload.user_id,
        "session_id": payload.session_id,
        "db": db,
        "user_role": None,
        "grouped_feedbacks": None,
        "summaries": None,
        "error": None,
        "error_code": None,
    }

    result = await agent.ainvoke(initial_state)

    error = result.get("error")
    if error:
        error_code = result.get("error_code", "internal_error")
        status_code = _ERROR_CODES.get(error_code, 500)
        raise HTTPException(status_code=status_code, detail=error)

    return FeedbackSummaryResponse(
        user_id=result["user_id"],
        session_id=result["session_id"],
        summaries=result["summaries"],
    )
