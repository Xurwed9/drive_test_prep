from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.official_sample import OfficialSample


class OfficialSampleTranslation(Base):
    __tablename__ = "official_sample_translations"

    __table_args__ = (
        UniqueConstraint(
            "official_sample_id",
            "language",
            name="uq_official_sample_translation_language",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    official_sample_id: Mapped[int] = mapped_column(
        ForeignKey("official_samples.id"),
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

    official_sample: Mapped["OfficialSample"] = relationship(
        back_populates="translations"
    )