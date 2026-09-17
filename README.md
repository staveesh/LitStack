<div align="center">

# 📚 LitStack

**A research knowledge base for serious readers.**

Turn a pile of PDFs into structured, retrievable knowledge — without losing your own thinking to AI noise.

[![Next.js](https://img.shields.io/badge/Next.js_14-black?logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL_+_pgvector-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Docker](https://img.shields.io/badge/Docker_Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose)

</div>

---

## The workflow

```
DISCOVER → TRIAGE → READ → EXTRACT → CONNECT → SYNTHESIZE → RESURFACE → WRITE
```

> **Papers are source material.** Research questions, claims, evidence, and open questions are the actual knowledge structure.

LitStack is not a PDF summarizer or "chat with your papers" tool. It is a system for turning a large literature collection into a knowledge base you can trust and retrieve from six months later.

---

## Features

### 📥 Inbox & Triage
Import papers from Zotero. Select a batch and run **AI Triage** — the AI receives each paper's title, abstract, and your active research questions, and returns:
- Relevance score
- Recommended action (`deep_read` / `skim` / `citation_only` / `ignore`)
- Rationale and which research questions it addresses
- A suggested reading intent

All recommendations are editable before you apply them. Nothing is silently committed.

### 🔄 Reading Workflow
Papers move through explicit states:

| Status | Meaning |
|---|---|
| `inbox` | Newly imported, not yet evaluated |
| `triaged` | Assessed, queued for reading |
| `skim` | Worth a quick pass |
| `deep_read` | Scheduled for careful reading |
| `read` | Done |
| `citation_only` | Relevant as a reference, not for reading |
| `archived` | Discarded from active queue |

### 🎯 Reading Intents
Before opening a paper for a deep read, record *why* you are reading it:

> *"Determine whether their runtime monitor is outside the agent's trust boundary and whether the agent can bypass it."*

Intents link to specific research questions and can be marked resolved with notes. The app nudges you to set one before every deep read.

### 🤖 AI Structured Extraction
After reading or uploading a PDF, AI extracts:
- Problem statement & research question
- Key idea, approach, and system architecture
- Threat model and assumptions
- Datasets, baselines, metrics, and results
- Limitations and future work
- Claims made by the authors

Every extracted field retains **provenance** — page number, section, and passage — so you can verify it against the source.

**AI extraction is always visually distinguished from your own notes.** The boundary is never blurred.

### 📝 Human Notes
Your interpretation lives in its own space, never overwritten by AI:

| Field | What to record |
|---|---|
| Why I care | Your motivation for reading this |
| What surprised me | Unexpected findings or approaches |
| What I don't believe | Skepticism, methodological concerns |
| Relation to my work | How it connects to your research |
| What I might cite this for | Specific uses in future writing |
| Unanswered questions | What the paper left open for you |
| Freeform notes | Anything else |

### 🔗 Claims & Evidence
Build and maintain a claim ledger:

```
CLAIM: "Deterministic transformations provide stronger guarantees than free-form LLM rewriting."

  ✅ Supporting:  Paper A — Section 4.2 (conf: 0.91)
                 Paper B — Table 3 (conf: 0.84)
  ❌ Contradicting: Paper C — Discussion (conf: 0.72)
  ⚠️  Qualifying:  Paper D — "only under adversarial settings"
```

AI suggests evidence links — you approve before anything is added.

### ❓ Research Questions & Open Questions
Research questions are **first-class entities**, not folders. Each question tracks its status (`active` / `partially_answered` / `answered` / `abandoned`) and links directly to papers and claims.

Open questions capture gaps: assumptions papers don't test, missing baselines, contradictory results, unexamined design spaces. AI can propose new open questions after processing a paper; you promote them to tracked entities.

### 🔬 Cross-Paper Synthesis
Select a set of papers and synthesize along any dimension — enforcement placement, threat models, evaluation methodology, datasets, findings. Outputs can include **comparison matrices**:

| System | Enforcement placement | Agent trusted? | Semantic LLM? | Stateful? |
|---|---|---|---|---|
| Paper A | Network-side | No | Yes | No |
| Paper B | Endpoint | Yes | No | Yes |

Save the result as a **Synthesis Note** linked to the source papers.

### 🔍 Hybrid Search
Retrieve knowledge with structured filters or natural language:

- *"Papers from 2024–2025 on LLM agent privacy"*
- *"Which papers evaluated privacy/utility tradeoffs?"*
- *"What evidence do I have for the claim that LLM rewriting can introduce new information?"*
- *"Papers supporting Claim X that I haven't deep-read yet"*

Search runs over titles, abstracts, extracted content, human notes, claims, evidence, and synthesis notes — combining semantic similarity with structured database filters.

### 🔁 Zotero Integration
Zotero stays the canonical bibliographic source. LitStack syncs metadata, citation keys, and PDF attachments, then layers research metadata on top without touching Zotero.

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Radix UI |
| Backend | Python 3, FastAPI, Pydantic v2 |
| Database | PostgreSQL + pgvector |
| AI | Anthropic / OpenAI / local OpenAI-compatible |
| PDF | PyMuPDF (page-aware extraction with section chunking) |
| Jobs | APScheduler (Zotero sync) |
| Deployment | Docker Compose |

---

## Quick start

**Prerequisites:** Docker and Docker Compose.

```bash
# 1. Clone and configure
git clone https://github.com/staveesh/LitStack
cd LitStack
cp .env.example .env
# Edit .env — add your Zotero and AI API keys

# 2. Start
make start

# 3. (Optional) Load demo data
docker compose exec backend python seed.py
```

App → `http://localhost:3000`  
API → `http://localhost:8000`

### Environment variables

```bash
# Zotero — get keys at https://www.zotero.org/settings/keys
ZOTERO_API_KEY=
ZOTERO_LIBRARY_ID=
ZOTERO_LIBRARY_TYPE=user        # or "group"
ZOTERO_COLLECTION_KEY=          # optional — limits sync to one collection
ZOTERO_SYNC_INTERVAL_MINUTES=300  # 0 to disable background sync

# AI — at least one required
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Optional: local OpenAI-compatible endpoint (e.g. LM Studio)
LOCAL_LLM_BASE_URL=
LOCAL_LLM_MODEL=

# Default AI provider: anthropic | openai | local
DEFAULT_AI_PROVIDER=anthropic

# PDF storage (Docker volume)
PDF_STORAGE_PATH=/data/pdfs
```

### Make targets

| Command | Action |
|---|---|
| `make start` | Start in production mode |
| `make dev` | Start with hot reload |
| `make stop` | Stop containers |
| `make reset` | Stop and wipe all data volumes |
| `make logs` | Follow container logs |

---

## Zotero sync

- Syncs on startup and every `ZOTERO_SYNC_INTERVAL_MINUTES` minutes.
- Set `ZOTERO_COLLECTION_KEY` to limit sync to one collection — find keys via `/api/zotero/collections`.
- Zotero metadata is **never overwritten** without an explicit user action.
- Research metadata (questions, claims, notes, evidence) lives only in LitStack's database and survives re-syncs.

---

## AI providers

Switch providers in the UI per-request, or set `DEFAULT_AI_PROVIDER` in `.env`. Every AI operation records:

- Model name and provider
- Prompt version
- Timestamp
- Source inputs
- Generated output and confidence

This makes AI-generated data auditable and replaceable.

> **AI outputs are always proposals.** The researcher approves before anything is written to the knowledge base.

---

## Design principles

1. **AI proposes; researcher approves** — no silent modifications to the knowledge base
2. **Hard boundary between AI and human** — extractions and notes are always visually distinct
3. **Provenance on everything** — every AI claim traces back to a page and passage
4. **Discard aggressively** — the system helps you cut the queue, not just grow it
5. **Optimize for retrieval six months later** — notes should answer "why did I care?" not just "what was this about?"
6. **Local-first** — runs entirely on your machine; external API calls are explicit and minimal

---

## Demo data

Running `seed.py` loads a sample project — *"Privacy Enforcement for LLM Agents"* — with:

- 4 research questions (enforcement placement, entitlement reasoning, semantic separation, privacy/utility tradeoffs)
- 3 claims with supporting, contradicting, and qualifying evidence
- Fake papers with extraction, human notes, reading intents, and open questions

This makes the intended workflow immediately tangible after installation.
