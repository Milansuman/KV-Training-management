from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Enum as SqlEnum

from models.entity import AccessLogMixIn, Entity

class ProgramRoles(Enum):
    STAFF = "STAFF"
    CANDIDATE = "CANDIDATE"

class ProgramPermission(Entity, AccessLogMixIn):
    __abstract__ = False
    __tablename__ = "program_permission"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    program_id: Mapped[int] = mapped_column(
        ForeignKey("program.id", ondelete="CASCADE")
    )
    role: Mapped[ProgramRoles] = mapped_column(
        SqlEnum(ProgramRoles),
        default=ProgramRoles.CANDIDATE
    )
