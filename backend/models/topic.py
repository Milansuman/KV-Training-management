from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text
from models.entity import Entity

if TYPE_CHECKING:
    from models.session import Session, session_topic

class Topic(Entity):
    __abstract__ = False
    __tablename__ = "topic"

    title: Mapped[str] = mapped_column(
        Text
    )
    sessions: Mapped[list["Session"]] = relationship(secondary="session_topic")
