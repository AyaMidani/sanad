from app.rag.answer import MODEL, SYSTEM_PROMPT, build_answer, client, to_search_result
from app.rag.search import hybrid_search

SEARCH_TOOL = {
    "name": "search_documents",
    "description": (
        "Search Dubai Islamic Bank fee documents. "
        "Returns up to 5 matching passages with page numbers. "
        "Use one search per fee you need. To compare a fee across "
        "customer segments, search once per segment. "
        "Leave segment empty to search all documents."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "What to search for, e.g. 'debit card replacement fee'",
            },
            "segment": {
                "type": "string",
                "enum": ["wajaha", "aayan", "standard", "business"],
                "description": "Customer segment to filter by",
            },
        },
        "required": ["question"],
    },
}


async def ask_agent(question: str, segment: str | None = None):
    if segment:
        question = f"Customer segment: {segment}.\nQuestion: {question}"
    messages = [{"role": "user", "content": question}]

    for _ in range(5):
        response = await client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=[SEARCH_TOOL],
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return build_answer(response)

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                chunks = await hybrid_search(
                    block.input["question"],
                    block.input.get("segment"),
                )
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": [to_search_result(chunk) for chunk in chunks],
                    }
                )

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    raise RuntimeError("Agent did not answer after 5 rounds")
