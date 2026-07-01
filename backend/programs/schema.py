from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class CreateProgramRequest(BaseModel):
    title: str
    description: str
    start_date: date
    end_date: date


    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be earlier than end_date")
        return self

class ProgramResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    start_date: date
    end_date: date
    created_at: datetime


class UpdateProgramRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date >= self.end_date
        ):
            raise ValueError("start_date must be earlier than end_date")
        return self


class ProgramProgressItem(BaseModel):
    id: int
    title: str
    description: str
    total_sessions: int
    completed_sessions: int
    created_at: datetime
    updated_at: datetime
    start_date: date
    end_date: date
