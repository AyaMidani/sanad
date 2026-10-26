from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed, DateTime, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    page: Mapped[int]
    source: Mapped[str]
    embedding: Mapped[list[float]] = mapped_column(Vector(1024))
    search_words: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', replace(text, '/', ' '))", persisted=True),
    )


class AskLog(Base):
    __tablename__ = "ask_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
