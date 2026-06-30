from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FeedbackSubmissionCreateRequest(BaseModel):
    user_id: int
    recipient_id: Optional[int] = None
    feedback_id: int
    text: str


class FeedbackSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recipient_id: Optional[int]
    feedback_id: int
    text: str
    submitted_at: datetime
