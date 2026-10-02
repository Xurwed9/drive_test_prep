from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.topic import Topic


class TopicTranslation(Base):
    __tablename__ = "topic_translations"

    __table_args__ = (
        UniqueConstraint(
            "topic_id",
            "language",
            name="uq_topic_translation_language",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
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

    review_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft",
    )

    topic: Mapped["Topic"] = relationship(
        back_populates="translations"
    )