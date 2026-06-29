from datetime import datetime

from pydantic import BaseModel, ConfigDict



class TopicCreateRequest(BaseModel):
    title: str


class TopicUpdateRequest(BaseModel):
    title: str


class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str


