from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Text

from models.entity import Entity

class Assignment(Entity):
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
