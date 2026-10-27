import json
from pathlib import Path

from app.db.models import Chunk
from app.db.session import SessionLocal
from app.rag.chunking import chunk_page
from app.rag.embeddings import embed_documents
from app.rag.extract import extract_pages

DOCUMENTS_FILE = Path("data/documents.json")


def segment_for(pdf_path: Path) -> str:
    segments = json.loads(DOCUMENTS_FILE.read_text(encoding="utf-8"))
    if pdf_path.name not in segments:
        raise ValueError(f"{pdf_path.name} is missing from data/documents.json")
    return segments[pdf_path.name]


async def ingest_pdf(pdf_path: Path) -> int:
    segment = segment_for(pdf_path)

    # 1. PDF → pages → text chunks
    text_chunks = []
    for page in extract_pages(pdf_path):
        text_chunks.extend(chunk_page(page))

    # 2. text chunks → embeddings
    texts = []
    for text_chunk in text_chunks:
        texts.append(text_chunk.text)
    embeddings = embed_documents(texts)

    # 3. save each chunk as a row
    async with SessionLocal() as session:
        for text_chunk, embedding in zip(text_chunks, embeddings):
            row = Chunk(
                text=text_chunk.text,
                page=text_chunk.page,
                source=pdf_path.name,
                segment=segment,
                embedding=embedding,
            )
            session.add(row)
        await session.commit()

    return len(text_chunks)
