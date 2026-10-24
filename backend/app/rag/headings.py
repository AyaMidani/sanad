from collections import Counter

import pymupdf


def read_lines(page: pymupdf.Page) -> list[tuple[str, float]]:
    lines = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = ""
            size = 0
            for span in line["spans"]:
                text += span["text"]
                size = max(size, span["size"])
            text = text.strip()
            if text:
                lines.append((text, round(size, 1)))
    return lines


def body_size(lines: list[tuple[str, float]]) -> float:
    counts = Counter(size for _, size in lines)
    return counts.most_common(1)[0][0]
