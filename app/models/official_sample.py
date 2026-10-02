from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.content_version import ContentVersion
    from app.models.source import Source
    from app.models.official_sample_translation import OfficialSampleTranslation

class OfficialSample(Base):
    __tablename__ = "official_samples"

    id: Mapped[int] = mapped_column(primary_key=True)

    content_version_id: Mapped[int] = mapped_column(
        ForeignKey("content_versions.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id"),
        nullable=True,
    )

    content_version: Mapped["ContentVersion"] = relationship()

    source: Mapped["Source | None"] = relationship()
    translations: Mapped[list["OfficialSampleTranslation"]] = relationship(
    back_populates="official_sample",
    cascade="all, delete-orphan",
    )