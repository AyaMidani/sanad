from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed
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
