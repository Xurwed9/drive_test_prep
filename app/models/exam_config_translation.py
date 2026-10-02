from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.exam_config import ExamConfig


class ExamConfigTranslation(Base):
    __tablename__ = "exam_config_translations"

    __table_args__ = (
        UniqueConstraint(
            "exam_config_id",
            "language",
            name="uq_exam_config_translation_language",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    exam_config_id: Mapped[int] = mapped_column(
        ForeignKey("exam_configs.id"),
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

    exam_config: Mapped["ExamConfig"] = relationship(
        back_populates="translations"
    )