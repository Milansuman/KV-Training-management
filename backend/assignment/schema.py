from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class AssignmentCreateRequest(BaseModel):
    title: str
    description: str
    session_id: int
    due_at: datetime

    @field_validator("due_at")
    @classmethod
    def validate_due_at(cls, value: datetime) -> datetime:
        if value <= datetime.now(tz=UTC):
            raise ValueError("due_at must be in the future")
        return value


class AssignmentUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    due_at: datetime | None = None

    @field_validator("due_at")
    @classmethod
    def validate_due_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value <= datetime.now(tz=UTC):
            raise ValueError("due_at must be in the future")
        return value


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    session_id: int
    due_at: datetime
    created_at: datetime
    updated_at: datetime