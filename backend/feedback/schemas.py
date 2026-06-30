from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from feedback_submission.schemas import FeedbackSubmissionResponse


class FeedbackSubmissionsBySessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    submissions: list[FeedbackSubmissionResponse]
