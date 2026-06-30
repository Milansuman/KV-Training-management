from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Date, Text

from models.entity import AccessLogMixIn, Entity

if TYPE_CHECKING:
    from models.session import Session
else:
    Session = "Session"

class Program(Entity, AccessLogMixIn):
    __abstract__ = False
    __tablename__ = "program"

    title: Mapped[str] = mapped_column(
        Text
    )
    description: Mapped[str] = mapped_column(
        Text
    )
    start_date: Mapped[date] = mapped_column(
        Date
    )
    end_date: Mapped[date] = mapped_column(
        Date
    )
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="program"
    )
