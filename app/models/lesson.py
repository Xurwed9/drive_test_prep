from sqlalchemy import ForeignKey, String, Text, Integer,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.topic import Topic
    from app.models.lesson_translation import LessonTranslation


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
    UniqueConstraint(
        "topic_id",
        "order",
        name="uq_lessons_topic_order",
    ),
)

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False,)
    title: Mapped[int] = mapped_column(String(200), nullable=False,)
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    topic: Mapped["Topic"] = relationship(back_populates="lessons")
    questions: Mapped[list["Question"]] = relationship(
    back_populates="lesson"
    )
    translations: Mapped[list["LessonTranslation"]] = relationship(
    back_populates="lesson",
    cascade="all, delete-orphan",
    )