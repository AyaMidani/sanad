from app.rag.answer import client

GRADER_MODEL = "claude-haiku-5-5"

GRADER_PROMPT = """You are grading an answer from a banking fees assistant.

Question:
{question}

Correct answer:
{expected}

Assistant's answer:
{answer}

Does the assistant's answer give the same fee information as the correct answer?
Ignore wording, language, and citation markers like [1].

Reply with exactly two lines:
Line 1: one word, CORRECT, PARTIAL, or WRONG
Line 2: one sentence explaining why"""


async def grade(question: str, expected: str, answer: str) -> tuple[str, str]:
    prompt = GRADER_PROMPT.format(question=question, expected=expected, answer=answer)
    response = await client.messages.create(
        model=GRADER_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    text = ""
    for block in response.content:
        if block.type == "text":
            text = block.text

    lines = text.strip().splitlines()
    verdict = lines[0].strip()
    reason = lines[1].strip() if len(lines) > 1 else ""
    return verdict, reason
