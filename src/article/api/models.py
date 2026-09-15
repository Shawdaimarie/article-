from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from article.api.db import Base


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_name: Mapped[str] = mapped_column(String(255), index=True)
    charter_name: Mapped[str] = mapped_column(String(255))
    charter_version: Mapped[str] = mapped_column(String(32))
    score: Mapped[float] = mapped_column(Float)
    passed: Mapped[int] = mapped_column(Integer)
    failed: Mapped[int] = mapped_column(Integer)
    skipped: Mapped[int] = mapped_column(Integer)
    results: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
