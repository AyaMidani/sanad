# Technical Decisions

## 001 — Python + FastAPI for the backend
**Decision:** Python with FastAPI, instead of Node.js.
**Why:** The tools this project depends on are strongest in Python: PDF extraction with page numbers (including Arabic text), local multilingual embedding models, and RAG evaluation libraries. FastAPI gives async support for concurrent LLM calls, request validation through type hints, and auto-generated API docs.
**Trade-off:** I'm faster in Node.js, so early development is slower.

## 002 — Project structure: the RAG pipeline is separate from the API
**Decision:** The RAG pipeline lives in `app/rag/` as plain Python with no dependency on FastAPI. `app/api/` is a thin HTTP layer that calls it. `api` may import from `rag`, never the reverse.
**Why:** The pipeline has three callers: the API, the evaluation script, and a future agent that uses retrieval as a tool. Keeping it independent means evals run directly, without starting a server.
**Trade-off:** Considered a feature-first layout (one folder per feature). At this size, layers are easier to navigate, and the boundary that matters is between the pipeline and the web layer.