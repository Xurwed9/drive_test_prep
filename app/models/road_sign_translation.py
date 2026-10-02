from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.road_sign import RoadSign


class RoadSignTranslation(Base):
    __tablename__ = "road_sign_translations"

    __table_args__ = (
        UniqueConstraint(
            "road_sign_id",
            "language",
            name="uq_road_sign_translation_language",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    road_sign_id: Mapped[int] = mapped_column(
        ForeignKey("road_signs.id"),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    review_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft",
    )

    road_sign: Mapped["RoadSign"] = relationship(
        back_populates="translations"
    )