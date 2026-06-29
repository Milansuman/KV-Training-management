from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text
from models.entity import Entity

from models.session import session_topic
if TYPE_CHECKING:
    from models.session import Session
class Topic(Entity):
    __abstract__ = False
    __tablename__ = "topic"

    title: Mapped[str] = mapped_column(
        Text
    )
    sessions: Mapped[list["Session"]] = relationship(
    secondary=session_topic,
    back_populates="topics"
)