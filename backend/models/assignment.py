from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import DateTime, Text

from models.entity import Entity, AccessLogMixIn

class Assignment(Entity, AccessLogMixIn):
    __abstract__ = False
    __tablename__ = "assignment"

    title: Mapped[str] = mapped_column(
        Text
    )
    description: Mapped[str] = mapped_column(
        Text
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("session.id")
    )
    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
