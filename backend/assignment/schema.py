from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssignmentCreateRequest(BaseModel):
    title: str
    description: str
    session_id: int
    due_at: datetime


class AssignmentUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    due_at: datetime | None = None


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    session_id: int
    due_at: datetime
    created_at: datetime
    updated_at: datetime