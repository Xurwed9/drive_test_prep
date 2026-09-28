from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.question import Question


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    page: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    )
    questions: Mapped[list["Question"]] = relationship(
    back_populates="source"
    )