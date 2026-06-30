from datetime import UTC, datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, DateTime

from db.connection import Base

class Entity(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=UTC)
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

class AccessLogMixIn:
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id")
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id")
    )
