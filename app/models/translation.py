from sqlalchemy import ForeignKey, String, Text,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.question import Question


class Translation(Base):
    __tablename__ = "translations"
    __table_args__ = (
    UniqueConstraint(
        "question_id",
        "language",
        name="uq_translations_question_language",
    ),
)

    id: Mapped[int] = mapped_column(primary_key=True)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    review_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    question: Mapped["Question"] = relationship(back_populates="translations")