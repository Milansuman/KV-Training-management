from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssignmentSubmissionCreateRequest(BaseModel):
    url: str
    user_id: int
    assignment_id: int


class AssignmentSubmissionUpdateRequest(BaseModel):
    url: str | None = None


class AssignmentSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    user_id: int
    assignment_id: int
    created_at: datetime
    updated_at: datetime