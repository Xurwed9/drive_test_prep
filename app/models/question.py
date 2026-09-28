from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.source import Source
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.translation import Translation
    from app.models.lesson import Lesson
    from app.models.source import Source
    from app.models.question_option import QuestionOption


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)

    content_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id"),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)

    correct_option_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    question_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    is_official: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id"),
        nullable=True,
    )

    lesson: Mapped["Lesson"] = relationship(
        back_populates="questions"
    )

    translations: Mapped[list["Translation"]] = relationship(
        back_populates="question"
    )

    source: Mapped["Source | None"] = relationship(
        back_populates="questions"
    )

    options: Mapped[list["QuestionOption"]] = relationship(
        back_populates="question"
    )