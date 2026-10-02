from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.lesson import Lesson
    from app.models.lesson_translation import LessonTranslation


class LessonTranslation(Base):
    __tablename__ = "lesson_translations"

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "language",
            name="uq_lesson_translation_language",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id"),
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

    lesson: Mapped["Lesson"] = relationship(
        back_populates="translations"
    )