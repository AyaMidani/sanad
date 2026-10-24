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

## 004 — Chunking: size-based, with section headings repeated
**Decision:** Cut each page into chunks of up to 800 characters on line boundaries, with a 2-line overlap. Detect section headings by relative font size (a line larger than the page's most common size), and repeat the current heading at the top of each chunk that starts mid-section.
**Why:** Without headings, a chunk split from the middle of a section lost the context of which product it belonged to, so rows with the same name under different products (e.g. "Liability Letter" for cards vs. for finance) looked almost identical to search. Measured on a 15-question golden set (10 English, 5 Arabic):

| | recall@5 | recall@1 |
|---|---|---|
| Size-based | 100% | 73% |
| Size-based + headings | 100% | 87% |

**Trade-off:** A fixed font-size threshold worked on one PDF but failed on the other, so the threshold is relative to each page. Headings don't carry across pages, so text at the top of a page that continues a section from the previous page gets no heading. Two questions still miss rank 1: one is a vocabulary gap (the PDF says "Covered & Charge Cards", never "credit card"), and one where a heading pulls in the wrong chunk ("personal finance" in the question matches the Personal Finance heading on page 7, while the answer is under Customer Services – Finance on page 8).

Size-based chunks (800 chars, 2-line overlap) lost their section heading when a section
was split across chunks, so the retriever couldn't tell apart rows with the same name
under different products (e.g. "Liability Letter" for cards vs. finance).

Fix: detect headings by relative font size (larger than the page's most common size),
and repeat the current heading at the top of each split chunk.

Measured on a 15-question golden set (10 English, 5 Arabic):

| | recall@5 | recall@1 |
|---|---|---|
| Size-based | 100% | 73% |
| Size-based + headings | 100% | 87% |

Remaining misses are vocabulary gaps, not chunking: the PDF says "Covered & Charge Cards",
never "credit card".
