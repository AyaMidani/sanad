import asyncio
import json
from pathlib import Path

from app.rag.search import hybrid_search

GOLDEN_SET = Path(__file__).parent / "golden_set.json"


async def main():
    questions = json.loads(GOLDEN_SET.read_text(encoding="utf-8"))
    hits = 0
    first_place = 0

    for q in questions:
        chunks = await hybrid_search(q["question"])
        found = [(chunk.source, chunk.page) for chunk in chunks]
        expected = (q["source"], q["expected_page"])

        if expected in found:
            position = found.index(expected) + 1
            hits += 1
            if position == 1:
                first_place += 1
            print(f"HIT  @{position}  {q['id']}")
        else:
            print("MISS     ", q["id"], "got:", found)
        await asyncio.sleep(21)

    total = len(questions)
    print(f"\nrecall@5: {hits}/{total} = {hits / total:.0%}")
    print(f"recall@1: {first_place}/{total} = {first_place / total:.0%}")


asyncio.run(main())
