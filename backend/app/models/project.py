from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    niche: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    description: Mapped[str] = mapped_column(String(512), default="", nullable=False)

    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)  # active|paused
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
