from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CreateProgramRequest(BaseModel):
    title: str
    description: str
    start_date: date
    end_date: date


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


class ProgramProgressItem(BaseModel):
    id: int
    title: str
    description: str
    total_sessions: int
    completed_sessions: int
    created_at: datetime
    updated_at: datetime
