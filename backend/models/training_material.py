from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Text

from models.entity import Entity

class TrainingMaterial(Entity):
    __abstract__ = False
    __tablename__ = "training_material"

    title: Mapped[str] = mapped_column(
        Text
    )
    url: Mapped[str] = mapped_column(
        Text
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("session.id")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id")
    )
