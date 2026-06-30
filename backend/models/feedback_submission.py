from datetime import datetime, UTC
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import DateTime, Text

from models.entity import AccessLogMixIn, Entity

class FeedbackSubmission(Entity, AccessLogMixIn):
    __abstract__ = False
    __tablename__ = "feedback_submission"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id")
    )
    recipient_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id")
    )
    feedback_id: Mapped[int] = mapped_column(
        ForeignKey("feedback.id")
    )
    text: Mapped[str] = mapped_column(
        Text
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=UTC)
    )
