from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class SessionCreateRequest(BaseModel):
    title: str
    description: str

    start_datetime: datetime
    end_datetime: datetime

    program_id: int

class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str 
class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    title: str
    description: str

    start_datetime: datetime
    end_datetime: datetime

    program_id: int

class SessionResponseWithTopics(SessionResponse):
    model_config = ConfigDict(from_attributes=True)
    topics: list[TopicResponse] = []

class SessionUpdateRequest(BaseModel):
    title: str
    description: str

    start_datetime: datetime
    end_datetime: datetime

    
    