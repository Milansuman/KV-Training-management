from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class SessionCreateRequest(BaseModel):
    title: str
    description: str

    start_datetime: datetime
    end_datetime: datetime

    program_id: int

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError(
                "end_datetime must be after start_datetime"
            )

        return self
    
class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    title: str
    description: str

    start_datetime: datetime
    end_datetime: datetime

    program_id: int

class SessionUpdateRequest(BaseModel):
    title: str
    description: str

    start_datetime: datetime
    end_datetime: datetime

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError(
                "End datetime must be greater than start datetime"
            )

        return self
    