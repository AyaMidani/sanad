from sqlalchemy import select, text

from app.db.models import Chunk
from app.db.session import SessionLocal
from app.rag.embeddings import embed_query

TOP_K = 5
RRF_K = 60


async def search(question: str, segment: str | None = None) -> list[Chunk]:
    question_vector = embed_query(question)
    statement = select(Chunk).order_by(Chunk.embedding.cosine_distance(question_vector))
    if segment:
        statement = statement.where(Chunk.segment.in_([segment, "all"]))
    async with SessionLocal() as session:
        result = await session.scalars(statement.limit(TOP_K))
        return list(result)


WORD_SEARCH_SQL = """
SELECT chunks.*
FROM chunks,
     to_tsquery('english', replace(plainto_tsquery('english', :q)::text, '&', '|')) AS query
WHERE search_words @@ query
  AND (CAST(:segment AS text) IS NULL OR segment IN (:segment, 'all'))
ORDER BY ts_rank(search_words, query) DESC
LIMIT :k
"""


async def word_search(question: str, segment: str | None = None) -> list[Chunk]:
    async with SessionLocal() as session:
        statement = select(Chunk).from_statement(
            text(WORD_SEARCH_SQL).bindparams(q=question, k=TOP_K, segment=segment)
        )
        result = await session.scalars(statement)
        return list(result)


async def hybrid_search(question: str, segment: str | None = None) -> list[Chunk]:
    meaning_results = await search(question, segment)
    word_results = await word_search(question, segment)

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
