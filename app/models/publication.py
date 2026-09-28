from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.content_version import ContentVersion


class PublicationAudit(Base):
    __tablename__ = "publication_audits"

    id: Mapped[int] = mapped_column(primary_key=True)

    content_version_id: Mapped[int] = mapped_column(
        ForeignKey("content_versions.id"),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    user_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
)

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    content_version: Mapped["ContentVersion"] = relationship(
    back_populates="audits"
)