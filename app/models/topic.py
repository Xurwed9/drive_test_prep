from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.content_version import ContentVersion
    from app.models.lesson import Lesson
    from app.models.topic_translation import TopicTranslation


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)

    content_version_id: Mapped[int] = mapped_column(
        ForeignKey("content_versions.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    lessons: Mapped[list["Lesson"]] = relationship(
    back_populates="topic"
    )
    content_version: Mapped["ContentVersion"] = relationship(
    back_populates="topics"
    )
    translations: Mapped[list["TopicTranslation"]] = relationship(
    back_populates="topic",
    cascade="all, delete-orphan",
    )