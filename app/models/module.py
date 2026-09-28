from sqlalchemy import ForeignKey, String

from app.db.base import Base
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.content_version import ContentVersion

class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True)

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    vehicle: Mapped["Vehicle"] = relationship(
    back_populates="modules"
)
    content_versions: Mapped[list["ContentVersion"]] = relationship(
    back_populates="module"
)