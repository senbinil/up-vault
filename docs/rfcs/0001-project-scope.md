# RFC 0001: up-vault Project Scope

- **Status:** Draft
- **Date:** 2026-10-05
- **Authors:** up-vault
- **Target:** MVP

## 1. Summary

up-vault is a RAG-based personal assistant for querying a user's own documents and knowledge.

The MVP focuses on a single workflow:

```text
Add documents
    ↓
Index documents
    ↓
Ask a question
    ↓
Retrieve relevant context
    ↓
Generate grounded answer
    ↓
Return sources
```

The goal is to build a small, reliable, and deliverable RAG system before introducing advanced assistant capabilities.

## 2. Problem

General-purpose LLMs do not have access to a user's private documents and personal knowledge.

up-vault allows users to make their own knowledge searchable using natural-language questions while grounding answers in the user's data.

## 3. Goals

The MVP must:

- Support document ingestion.
- Extract text from supported documents.
- Split documents into chunks.
- Generate embeddings.
- Store and retrieve embeddings.
- Answer questions using retrieved context.
- Return source references.
- Provide a simple API.
- Run locally using Python and `uv`.

## 4. Non-Goals

The MVP will not include:

- Autonomous agents.
- Tool calling.
- Web search.
- Voice interfaces.
- Image understanding.
- OCR.
- Knowledge graphs.
- Advanced memory systems.
- Fine-tuning.
- Multi-agent workflows.
- Multiple vector databases.
- Complex authentication.
- Multi-tenant support.
- Distributed job processing.

These may be considered after the MVP.

## 5. MVP Scope

### In scope

- Python application
- `uv` project management
- FastAPI API
- PostgreSQL + pgvector
- Markdown documents
- Plain-text documents
- Embeddings
- Vector similarity search
- LLM answer generation
- Source attribution
- Basic tests
- Basic RAG evaluation

### Out of scope

Everything not explicitly listed above.

## 6. Success Criteria

The MVP is complete when a user can:

1. Upload a supported document.
2. Successfully index the document.
3. Ask a question about its contents.
4. Receive an answer grounded in the document.
5. See the source used for the answer.
6. Receive an explicit "insufficient information" response when relevant context is unavailable.

## 7. Technology

| Area | Choice |
|---|---|
| Language | Python |
| Package manager | uv |
| API | FastAPI |
| Database | PostgreSQL |
| Vector search | pgvector |
| Embeddings | Single provider |
| LLM | Single provider |
| Testing | pytest |

## 8. MVP Milestones

### M1 — Foundation

- Initialize project.
- Configure `uv`.
- Add FastAPI.
- Configure PostgreSQL.
- Establish testing setup.

### M2 — Ingestion

- Upload documents.
- Extract text.
- Chunk text.
- Generate embeddings.
- Store chunks and embeddings.

### M3 — RAG

- Embed queries.
- Retrieve relevant chunks.
- Build context.
- Generate answers.
- Return sources.

### M4 — Hardening

- Error handling.
- Integration tests.
- Basic RAG evaluation.
- Documentation.
- Local setup instructions.

## 9. Guiding Principle

> Build the smallest useful RAG system first.

Features should not be added to the MVP unless they are required to prove the core workflow.