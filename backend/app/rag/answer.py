import anthropic

from app.core.config import settings
from app.db.models import Chunk
from app.rag.search import search

MODEL = "claude-haiku-5-5"

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


def to_search_result(chunk: Chunk) -> dict:
    return {
        "type": "search_result",
        "source": chunk.source,
        "title": f"Page {chunk.page}",
        "content": [{"type": "text", "text": chunk.text}],
        "citations": {"enabled": True},
    }


async def ask(question: str):
    chunks = await search(question)
    boxes = [to_search_result(chunk) for chunk in chunks]

    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": boxes + [{"type": "text", "text": question}],
            }
        ],
    )
    return response
