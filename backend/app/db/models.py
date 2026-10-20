from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    page: Mapped[int]
    embedding: Mapped[list[float]] = mapped_column(Vector(1024))
