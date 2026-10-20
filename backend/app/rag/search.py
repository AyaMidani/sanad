from sqlalchemy import select

from app.db.models import Chunk
from app.db.session import SessionLocal
from app.rag.embeddings import embed_query

TOP_K = 5


async def search(question: str) -> list[Chunk]:
    question_vector = embed_query(question)

    async with SessionLocal() as session:
        query = (
            select(Chunk)
            .order_by(Chunk.embedding.cosine_distance(question_vector))
            .limit(TOP_K)
        )
        result = await session.scalars(query)
        return list(result)
