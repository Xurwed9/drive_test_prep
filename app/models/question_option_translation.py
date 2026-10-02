from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.question_option import QuestionOption


class QuestionOptionTranslation(Base):
    __tablename__ = "question_option_translations"

    __table_args__ = (
        UniqueConstraint(
            "question_option_id",
            "language",
            name="uq_question_option_translation_language",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    question_option_id: Mapped[int] = mapped_column(
        ForeignKey("question_options.id"),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    review_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft",
    )

    question_option: Mapped["QuestionOption"] = relationship(
        back_populates="translations"
    )