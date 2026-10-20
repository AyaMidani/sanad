from dataclasses import dataclass
from pathlib import Path

import pymupdf

from app.rag.arabic import fix_lam_alef


@dataclass
class Page:
    number: int
    text: str


def extract_pages(pdf_path: Path) -> list[Page]:
    pages = []
    with pymupdf.open(pdf_path) as doc:
        for index, page in enumerate(doc):
            text = fix_lam_alef(page.get_text())
            pages.append(Page(number=index + 1, text=text))
    return pages
