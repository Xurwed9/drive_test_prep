from sqlalchemy import String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.content_version import ContentVersion


class State(Base):
    __tablename__ = 'states'
    __table_args__ = (
        CheckConstraint(
            "status IN ('available', 'coming_soon')",
            name="ck_states_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    content_versions: Mapped[list["ContentVersion"]] = relationship(
    back_populates="state"
)