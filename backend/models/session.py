from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import DateTime, Text

from db.connection import Base
from models.entity import Entity

if TYPE_CHECKING:
    from models.program import Program
    from models.topic import Topic

session_topic = Table(
    "session_topic",
    Base.metadata,
    Column("session_id", ForeignKey("session.id", ondelete="CASCADE")),
    Column("topic_id", ForeignKey("topic.id", ondelete="CASCADE"))
)

class Session(Entity):
    __abstract__ = False
    __tablename__ = "session"

    title: Mapped[str] = mapped_column(
        Text
    )
    description: Mapped[str] = mapped_column(
        Text
    )
    start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    end_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    program_id: Mapped[int] = mapped_column(
        ForeignKey("program.id", ondelete="CASCADE")
    )
    program: Mapped["Program"] = relationship(back_populates="sessions")
    topics: Mapped[list["Topic"]] = relationship(
    secondary=session_topic,
    back_populates="sessions"
)
