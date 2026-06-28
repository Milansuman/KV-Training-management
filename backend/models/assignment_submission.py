from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Text

from models.entity import Entity

class AssignmentSubmission(Entity):
    __abstract__ = False
    __tablename__ = "assignment_submission"

    url: Mapped[str] = mapped_column(
        Text
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id")
    )
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignment.id")
    )
