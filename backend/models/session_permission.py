from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Enum as SqlEnum

from models.entity import AccessLogMixIn, Entity

class SessionRoles(Enum):
    TRAINER = "TRAINER"
    MODERATOR = "MODERATOR"
    CANDIDATE = "CANDIDATE"

class SessionPermission(Entity, AccessLogMixIn):
    __abstract__ = False
    __tablename__ = "session_permission"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("session.id", ondelete="CASCADE")
    )
    role: Mapped[SessionRoles] = mapped_column(
        SqlEnum(SessionRoles),
        default=SessionRoles.CANDIDATE
    )
