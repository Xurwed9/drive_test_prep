from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.content_version import ContentVersion
    from app.models.source import Source
    from app.models.road_sign_translation import RoadSignTranslation



class RoadSign(Base):
    __tablename__ = "road_signs"
    id: Mapped[int] = mapped_column(primary_key=True)
    content_version_id: Mapped[int] = mapped_column(ForeignKey("content_versions.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    content_version: Mapped["ContentVersion"] = relationship(back_populates="road_signs")
    source: Mapped["Source | None"] = relationship()
    translations: Mapped[list["RoadSignTranslation"]] = relationship(
        back_populates="road_sign",
        cascade="all, delete-orphan",
    )