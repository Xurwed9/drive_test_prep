from sqlalchemy import String
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.module import Module
    from app.models.content_version import ContentVersion


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    modules: Mapped[list["Module"]] = relationship(
    back_populates="vehicle"
)
    content_versions: Mapped[list["ContentVersion"]] = relationship(
        back_populates="vehicle"
    )