import asyncio
import json
from collections import Counter
from pathlib import Path

from app.rag.agent import ask_agent
from app.rag.answer import ask
from evals.grader import grade

GOLDEN_SET = Path(__file__).parent / "golden_set.json"
USE_AGENT = True


async def main():
    questions = json.loads(GOLDEN_SET.read_text(encoding="utf-8"))
    correct = 0
    verdicts = Counter()

    for q in questions:
        if USE_AGENT:
            answer = await ask_agent(q["question"], q.get("segment"))
        else:
            answer = await ask(q["question"], q.get("segment"))
        cited = [(source.file, source.title) for source in answer.sources]
        expected = (q["source"], f"Page {q['expected_page']}")

        if expected in cited:
            correct += 1
            print("CITED  ", q["id"])
        else:
            print("WRONG  ", q["id"], "cited:", cited)
            print("   TEXT:", answer.text)

        verdict, reason = await grade(q["question"], q["expected_answer"], answer.text)
        verdicts[verdict] += 1
        print("   ", verdict, "-", reason)

    total = len(questions)
    print("\nmode:", "agent" if USE_AGENT else "normal")
    print(f"\ncitation accuracy: {correct}/{total} = {correct / total:.0%}")
    print(
        f"answers: {verdicts['CORRECT']} correct, {verdicts['PARTIAL']} partial, {verdicts['WRONG']} wrong"
    )


asyncio.run(main())
