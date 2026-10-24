from dataclasses import dataclass
from pathlib import Path

import pymupdf

from app.rag.arabic import fix_lam_alef
from app.rag.headings import body_size, read_lines  # new


@dataclass
class Page:
    number: int
    text: str
    headings: list[str]  # new


def extract_pages(pdf_path: Path) -> list[Page]:
    pages = []
    with pymupdf.open(pdf_path) as doc:
        for index, page in enumerate(doc):
            text = fix_lam_alef(page.get_text())

            lines = read_lines(page)  # new
            body = body_size(lines)  # new
            headings = []  # new
            for line_text, size in lines:  # new
                if size > body:  # new
                    headings.append(fix_lam_alef(line_text))  # new

            pages.append(Page(number=index + 1, text=text, headings=headings))
    return pages
