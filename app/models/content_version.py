from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String,UniqueConstraint, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.topic import Topic
    from app.models.publication import PublicationAudit
    from app.models.state import State
    from app.models.vehicle import Vehicle
    from app.models.module import Module
    from app.models.road_sign import RoadSign
    from app.models.official_sample import OfficialSample


class ContentVersion(Base):
    __tablename__ = "content_versions"

    __table_args__ = (
    UniqueConstraint(
        "state_id",
        "vehicle_id",
        "module_id",
        "version",
        name="uq_content_versions_scope_version",
    ),
    CheckConstraint(
        "status IN ("
        "'draft', "
        "'source_verified', "
        "'translation_pending', "
        "'translation_completed', "
        "'native_review', "
        "'approved', "
        "'published'"
        ")",
        name="ck_content_versions_status",
    ),
)

    id: Mapped[int] = mapped_column(primary_key=True)

    state_id: Mapped[int] = mapped_column(
        ForeignKey("states.id"),
        nullable=False,
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"),
        nullable=False,
    )

    module_id: Mapped[int | None] = mapped_column(
        ForeignKey("modules.id"),
        nullable=True,
    )

    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    package_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    checksum: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    package_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    minimum_app_version: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
)
    topics: Mapped[list["Topic"]] = relationship(
    back_populates="content_version"
    )
    audits: Mapped[list["PublicationAudit"]] = relationship(
    back_populates="content_version"
    )
    state: Mapped["State"] = relationship(
    back_populates="content_versions"
)
    vehicle: Mapped["Vehicle"] = relationship(
    back_populates="content_versions"
)
    module: Mapped["Module | None"] = relationship(
    back_populates="content_versions"
)
    road_signs: Mapped[list["RoadSign"]] = relationship(
    back_populates="content_version"
)
    official_samples: Mapped[list["OfficialSample"]] = relationship(
    back_populates="content_version"
)