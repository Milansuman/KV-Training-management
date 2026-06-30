from enum import Enum
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Enum as SqlEnum, Text

from models.entity import Entity

class FeedbackType(Enum):
    TEXT="TEXT"
    FORM="FORM"

class Feedback(Entity):
    __abstract__ = False
    __tablename__ = "feedback"

    session_id: Mapped[int] = mapped_column(
        ForeignKey("session.id")
    )
    type: Mapped[FeedbackType] = mapped_column(
        SqlEnum(FeedbackType)
    )
    url: Mapped[Optional[str]] = mapped_column(
        Text
    )
