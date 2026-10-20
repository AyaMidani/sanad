from dataclasses import dataclass

from app.rag.extract import Page

MAX_CHARS = 800
OVERLAP_LINES = 2


@dataclass
class Chunk:
    text: str
    page: int


def chunk_page(page: Page) -> list[Chunk]:
    chunks = []
    current_lines = []

    for line in page.text.splitlines():
        if line.strip() == "":
            continue

        current_text = "\n".join(current_lines)
        if current_lines and len(current_text) + len(line) > MAX_CHARS:
            chunks.append(Chunk(text=current_text, page=page.number))
            current_lines = current_lines[-OVERLAP_LINES:]

        current_lines.append(line)

    if current_lines:
        chunks.append(Chunk(text="\n".join(current_lines), page=page.number))

    return chunks
