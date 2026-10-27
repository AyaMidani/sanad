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

## 005 — Evaluation: retrieval, citation, and model-graded answers
**Decision:** Evaluate Sanad on a 15-question golden set (10 English, 5 Arabic, including trap questions where the same fee name appears under different products). Three checks: retrieval (is the right page in the top 5, and at rank 1), citation (did Claude cite the right page, checked by code), and answer correctness (graded by Claude Haiku as CORRECT, PARTIAL or WRONG against a reference answer).
**Why:** Each check catches a different failure. Retrieval failures can't be fixed by the prompt, and answer failures can't be fixed by chunking, so they're measured separately. The grader compares meaning, not text, because a correct answer can be phrased many ways and in either language.

Results, before and after changing the system prompt:

| | Correct | Partial | Wrong | Cited right page |
|---|---|---|---|---|
| Original prompt | 12 | 2 | 1 | 100% |
| Revised prompt (3 runs) | 13–14 | 1–2 | 0 | 93% |

The original prompt said "do not add details the search results do not state." Claude read that as forbidding it from connecting a customer's words ("credit card") to the bank's section names ("Covered & Charge Cards"), so it found the right fee and refused to commit. The revised prompt tells it to match by meaning and use the document's section name, to list each case only when the customer didn't say which product, and to never write file names in the text, so sources come only through citations.

Two bugs were found by the eval along the way: the grader returned no verdict because thinking used its whole token budget (fixed by disabling thinking for the grader), and Arabic answers were cut off for the same reason (fixed by raising `max_tokens` from 1024 to 4096).

**Trade-off:** 15 questions is small. One answer flipping between identical runs moves the score by 7%, so changes were only accepted if they held across more than one run, and prompt tuning stopped once results reached run-to-run noise, to avoid fitting the prompt to these exact questions. Known limitations, both in the data rather than the prompt:
- The Wajaha PDF shows fees with the new dirham symbol, which extraction reads as the letter "D" (`D105.00`, sometimes `D 175`). Fixed at extraction by converting "D" followed by a number into "AED".
- The Murabaha refund rule in the Home Finance PDF is missed in every run, likely because that Arabic table cell is scrambled during extraction.

## 006 — Filter search by customer segment
**Decision:** Each chunk stores a `segment` (wajaha, aayan, standard, business, or all), set at ingest from `data/documents.json`. Search only looks at the customer's segment plus shared documents. The customer picks their segment in the chat.
**Why:** Adding 7 more DIB documents dropped recall@1 from 87% to 47%. The same fees appear in several customer schedules (Wajaha, Aayan, standard), so they competed for the top results. With the filter, recall@1 went to 80%, recall@5 to 93%, and 12/15 answers were fully correct.
**Trade-off:** Every new PDF needs one line in `documents.json`. The segment is a fact from the bank, so it's set by hand instead of guessed by a model.
**Tried and dropped:** Contextual retrieval (Claude writes a description at the top of each chunk). Every card chunk got "credit card" in its description, so the word stopped telling chunks apart, and recall@5 fell to 73%.
