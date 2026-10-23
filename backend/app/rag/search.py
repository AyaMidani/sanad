from sqlalchemy import select, text

from app.db.models import Chunk
from app.db.session import SessionLocal
from app.rag.embeddings import embed_query

TOP_K = 5

RRF_K = 60

WORD_SEARCH_SQL = """
SELECT chunks.*
FROM chunks,
     to_tsquery('english', replace(plainto_tsquery('english', :q)::text, '&', '|')) AS query
WHERE search_words @@ query
ORDER BY ts_rank(search_words, query) DESC
LIMIT :k
"""


async def word_search(question: str) -> list[Chunk]:
    async with SessionLocal() as session:
        statement = select(Chunk).from_statement(
            text(WORD_SEARCH_SQL).bindparams(q=question, k=TOP_K)
        )
        result = await session.scalars(statement)
        return list(result)


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


async def hybrid_search(question: str) -> list[Chunk]:
    meaning_results = await search(question)
    word_results = await word_search(question)

    points = {}
    chunks_by_id = {}

    for results in (meaning_results, word_results):
        for position, chunk in enumerate(results, start=1):
            points[chunk.id] = points.get(chunk.id, 0) + 1 / (RRF_K + position)
            chunks_by_id[chunk.id] = chunk

    best_ids = sorted(points, key=points.get, reverse=True)[:TOP_K]

    final = []
    for chunk_id in best_ids:
        final.append(chunks_by_id[chunk_id])
    return final
