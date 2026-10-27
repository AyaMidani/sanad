from dataclasses import dataclass

import anthropic

from app.core.config import settings
from app.db.models import Chunk
from app.rag.search import hybrid_search

MODEL = "claude-haiku-5-5"

SYSTEM_PROMPT = """You are Sanad, an assistant that answers questions about bank fees and charges.

Rules:
- Answer only from the search results provided. Do not use outside knowledge.
- Back every fact (fees, amounts, conditions) with a citation.
- Never write file names or page numbers in your answer. Sources are attached through citations only.
- If the search results do not contain the answer, say so clearly. Do not guess.
- Customers use everyday words, but the documents use the bank's own product and section names. If a section clearly matches what the customer is asking about, answer with its fee directly and use the section's name from the document.
- DIB calls its credit cards "Covered Cards" (بطاقات مغطاة). Treat questions about credit cards as questions about Covered Cards.
- If the fee differs by product or contract type and the customer didn't say which one, list each case. If the customer named one, answer only for that one.
- Answer in the same language as the question.
- Keep answers short and direct."""

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


@dataclass
class Source:
    number: int
    file: str
    title: str


@dataclass
class Answer:
    text: str
    sources: list[Source]


def build_answer(response) -> Answer:
    parts = []
    source_numbers = {}

    for block in response.content:
        if block.type != "text":
            continue

        parts.append(block.text)

        for citation in block.citations or []:
            key = (citation.source, citation.title)
            if key not in source_numbers:
                source_numbers[key] = len(source_numbers) + 1
            marker = f" [{source_numbers[key]}]"
            if not parts[-1].endswith(marker):
                parts.append(marker)

    sources = []
    for key, number in source_numbers.items():
        file, title = key
        sources.append(Source(number=number, file=file, title=title))

    return Answer(text="".join(parts), sources=sources)


def to_search_result(chunk: Chunk) -> dict:
    return {
        "type": "search_result",
        "source": chunk.source,
        "title": f"Page {chunk.page}",
        "content": [{"type": "text", "text": chunk.text}],
        "citations": {"enabled": True},
    }


async def ask(question: str) -> Answer:
    chunks = await hybrid_search(question)
    boxes = [to_search_result(chunk) for chunk in chunks]

    response = await client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": boxes + [{"type": "text", "text": question}],
            }
        ],
    )
    return build_answer(response)
