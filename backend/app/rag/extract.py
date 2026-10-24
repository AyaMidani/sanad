from dataclasses import dataclass
from pathlib import Path

import pymupdf

from app.rag.arabic import fix_lam_alef
from app.rag.headings import body_size, read_lines


@dataclass
class Page:
    number: int
    text: str
    headings: list[str]


def extract_pages(pdf_path: Path) -> list[Page]:
    pages = []
    with pymupdf.open(pdf_path) as doc:
        for index, page in enumerate(doc):
            text = fix_lam_alef(page.get_text())

            lines = read_lines(page)
            body = body_size(lines)
            headings = []
            for line_text, size in lines:
                if size > body:
                    headings.append(fix_lam_alef(line_text))

            pages.append(Page(number=index + 1, text=text, headings=headings))
    return pages
