from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Boolean, Text

from models.entity import Entity

class User(Entity):
    __abstract__ = False
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        Text
    )
    display_name: Mapped[str] = mapped_column(
        Text
    )
    email: Mapped[str] = mapped_column(
        Text,
        unique=True
    )
    password: Mapped[str | None] = mapped_column(
        Text
    )
    google_sub: Mapped[str | None] = mapped_column(
        Text,
        unique=True
    )
    nonce: Mapped[str | None] = mapped_column(
        Text,
        default=None
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
