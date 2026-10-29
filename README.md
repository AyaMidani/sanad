# Sanad · سند

A bilingual (Arabic / English) assistant that answers questions about Dubai Islamic Bank fees, using only DIB's public documents, with a citation to the exact PDF page for every answer.

**Live:** [sanad-kappa-nine.vercel.app](https://sanad-kappa-nine.vercel.app)

## What it does

- **Cited answers.** Every fee in an answer links to the PDF and page it came from.
- **Arabic and English.** Ask in either language; an Arabic question can be answered from an English document.
- **No guessing.** If the documents don't contain the answer, Sanad says so.
- **Customer type.** Wajaha, Aayan, standard and business customers pay different fees for the same service. The customer can pick their type, and Sanad searches their schedule plus the documents shared by everyone.
- **Comparisons and second tries.** Claude decides which searches to run, so it can compare a fee across customer types ("Is replacing a debit card cheaper for Wajaha than for standard?"), or search again with different words when the first search misses.

Sanad covers 9 current DIB documents (October 2026): five schedules of charges, two card Key Facts Statements, and two warnings documents.

## How it works

```
PDF → pages → chunks (+ section headings) → Voyage embeddings → Postgres (pgvector + full-text)
                                                                       ↓
question → Claude decides what to search (agent, up to 5 rounds)
                ↓                                   ↑
          hybrid search (meaning + keywords, merged with RRF, filtered by customer type)
                                                                       ↓
                               Claude answers from the search results, with page citations
```

- **Ingestion:** PyMuPDF extracts each page. Arabic letter-order errors and the new dirham symbol are fixed during extraction. Pages are cut into 800-character chunks, and each chunk keeps its section heading, detected by font size.
- **Search:** vector search (Voyage `voyage-4`) and Postgres full-text search run side by side and are merged with Reciprocal Rank Fusion.
- **Agent:** Claude gets hybrid search as a tool. It chooses the search words and customer type, runs as many searches as the question needs, then answers. A one-search mode is kept behind a backend switch for comparison.
- **Answering:** Claude receives the chunks as search results with citations enabled, so page numbers come from the API, not from generated text.

## Evaluation

A 15-question golden set (10 English, 5 Arabic), including trap questions where the same fee name appears under different products.

| Check | Result |
|---|---|
| Right page in top 5 (recall@5) | 93% |
| Right page ranked first (recall@1) | 80% |
| Claude cited the right page | 100% (one-search mode: 87%) |
| Answers graded correct by Claude Haiku | 13 of 15, 2 partial, 0 wrong (one-search mode: 12, 2 partial, 1 wrong) |

Every design choice, including what was tried and dropped and why, is recorded with its numbers in [DECISIONS.md](DECISIONS.md).

## Stack

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL + pgvector, Voyage AI, Claude API
**Frontend:** React, TypeScript, Vite
**Hosting:** Vercel (frontend and backend), Neon (Postgres)

## Run it locally

You need Docker, Python 3.14, Node.js, and API keys for Anthropic and Voyage AI.

```bash
# database
docker compose up -d

# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then add your API keys
alembic upgrade head
uvicorn app.main:app --reload
```

Put DIB PDFs in `backend/data/pdfs/`, list each one with its customer type in `backend/data/documents.json`, and ingest them:

```bash
python -c "
import asyncio
from pathlib import Path
from app.rag.ingest import ingest_pdf

for path in sorted(Path('data/pdfs').glob('*.pdf')):
    print(path.name, asyncio.run(ingest_pdf(path)), 'chunks saved')
"
```

```bash
# frontend
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Run the evaluation from `backend`:

```bash
python -m evals.run_retrieval
python -m evals.run_answers
```

`run_answers` uses the agent by default. Set `USE_AGENT = False` in `evals/run_answers.py` to evaluate the one-search mode.

## About

Built by [Aya Mydani](https://linkedin.com/in/aya-mydani). Before this project I worked on document generation for Dubai Islamic Bank at Dtech, including the same kind of fee schedules Sanad reads.
