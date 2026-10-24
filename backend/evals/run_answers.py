import asyncio
import json
from pathlib import Path

from app.rag.answer import ask

GOLDEN_SET = Path(__file__).parent / "golden_set.json"


async def main():
    questions = json.loads(GOLDEN_SET.read_text(encoding="utf-8"))
    correct = 0

    for q in questions:
        answer = await ask(q["question"])
        cited = [(source.file, source.title) for source in answer.sources]
        expected = (q["source"], f"Page {q['expected_page']}")

        if expected in cited:
            correct += 1
            print("CITED  ", q["id"])
        else:
            print("WRONG  ", q["id"], "cited:", cited)
        print("   ", answer.text)
        await asyncio.sleep(21)

    total = len(questions)
    print(f"\ncitation accuracy: {correct}/{total} = {correct / total:.0%}")


asyncio.run(main())
