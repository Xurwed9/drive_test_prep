from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base



class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="editor")
    preferred_language: Mapped[str] = mapped_column(
    String(5),
    default="en",
    nullable=False,
    )