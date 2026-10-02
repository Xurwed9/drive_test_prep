from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.question_option_translation import QuestionOptionTranslation


class QuestionOption(Base):
    __tablename__ = "question_options"

    __table_args__ = (
        UniqueConstraint(
            "question_id",
            "option_id",
            name="uq_question_options_question_option",
        ),
        UniqueConstraint(
            "question_id",
            "order",
            name="qu_question_options_question_order",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"), nullable=False,
    )
    option_id: Mapped[str] = mapped_column(String(50), nullable=False,)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False,)
    question: Mapped["Question"] = relationship(back_populates="options")
    translations: Mapped[list["QuestionOptionTranslation"]] = relationship(
    back_populates="question_option",
    cascade="all, delete-orphan",
    )