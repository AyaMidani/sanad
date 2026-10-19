# Technical Decisions

## 001 — Python + FastAPI for the backend
**Decision:** Python with FastAPI, instead of Node.js.
**Why:** The tools this project depends on are strongest in Python: PDF extraction with page numbers (including Arabic text), local multilingual embedding models, and RAG evaluation libraries. FastAPI gives async support for concurrent LLM calls, request validation through type hints, and auto-generated API docs.
**Trade-off:** I'm faster in Node.js, so early development is slower.

## 002 — Project structure: the RAG pipeline is separate from the API
**Decision:** The RAG pipeline lives in `app/rag/` as plain Python with no dependency on FastAPI. `app/api/` is a thin HTTP layer that calls it. `api` may import from `rag`, never the reverse.
**Why:** The pipeline has three callers: the API, the evaluation script, and a future agent that uses retrieval as a tool. Keeping it independent means evals run directly, without starting a server.
**Trade-off:** Considered a feature-first layout (one folder per feature). At this size, layers are easier to navigate, and the boundary that matters is between the pipeline and the web layer.

## 003 — PostgreSQL + pgvector for storage and search
**Decision:** PostgreSQL with the pgvector extension, run locally with Docker Compose.
**Why:** Hybrid search needs both vector similarity and keyword search. Postgres does keyword search natively (full-text search) and pgvector adds vector search, so chunks, page numbers, embeddings and both search types live in one table and one query.
**Trade-off:** Dedicated vector databases (Pinecone, Qdrant) can be faster at very large scale, but would mean running two stores and keeping them in sync. At this project's scale, one database is simpler. Only the database runs in Docker during development; the backend runs from a local venv for faster iteration and will be containerised at deployment.
