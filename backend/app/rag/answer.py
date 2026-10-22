import anthropic

from app.core.config import settings
from app.db.models import Chunk
from app.rag.search import search

MODEL = "claude-haiku-5-5"

SYSTEM_PROMPT = """You are Sanad, an assistant that answers questions about bank fees and charges.

Rules:
- Answer only from the search results provided. Do not use outside knowledge.
- Back every fact (fees, amounts, conditions) with a citation.
- If the search results do not contain the answer, say so clearly. Do not guess.
- Do not add details the search results do not state, such as product names.
- Answer in the same language as the question.
- Keep answers short and direct."""

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
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": boxes + [{"type": "text", "text": question}],
            }
        ],
    )
    return response
