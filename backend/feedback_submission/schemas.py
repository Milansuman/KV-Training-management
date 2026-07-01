from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class FeedbackSubmissionCreateRequest(BaseModel):
    user_id: int
    recipient_id: Optional[int] = None
    feedback_id: int
    text: str

    @model_validator(mode="after")
    def validate_recipient(self):
        if (
            self.recipient_id is not None
            and self.user_id == self.recipient_id
        ):
            raise ValueError(
                "user_id and recipient_id cannot be the same"
            )

        return self


class FeedbackSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recipient_id: Optional[int]
    feedback_id: int
    text: str
    submitted_at: datetime
