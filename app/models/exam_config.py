from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.content_version import ContentVersion
    from app.models.exam_config_translation import ExamConfigTranslation


class ExamConfig(Base):
    __tablename__ = "exam_configs"

    id: Mapped[int] = mapped_column(primary_key=True)

    content_version_id: Mapped[int] = mapped_column(
        ForeignKey("content_versions.id"),
        nullable=False,
        unique=True,
    )

    question_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    passing_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    time_limit_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    max_mistakes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    content_version: Mapped["ContentVersion"] = relationship()
    translations: Mapped[list["ExamConfigTranslation"]] = relationship(
        back_populates="exam_config",
        cascade="all, delete-orphan",
    )