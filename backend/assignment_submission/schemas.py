from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class AssignmentSubmissionCreateRequest(BaseModel):
    url: HttpUrl
    user_id: int
    assignment_id: int



class AssignmentSubmissionUpdateRequest(BaseModel):
    url: HttpUrl | None = None




class AssignmentSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    url: HttpUrl
    user_id: int
    assignment_id: int
    created_at: datetime
    updated_at: datetime