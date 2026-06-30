from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Text

from models.entity import AccessLogMixIn, Entity

class AssignmentSubmission(Entity, AccessLogMixIn):
    __abstract__ = False
    __tablename__ = "assignment_submission"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "assignment_id",
            name="uq_assignment_submission_user_assignment",
        ),
    )
    url: Mapped[str] = mapped_column(
        Text
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id")
    )
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignment.id")
    )
