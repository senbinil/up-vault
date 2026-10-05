# AGENTS.md

Guidance for AI coding agents working in the up-vault repository.

## Project Overview

up-vault is a RAG-based personal assistant for querying a user's own documents.
It ingests documents, indexes them, retrieves relevant context, and generates
grounded answers with source attribution.

**Current state:** Early scaffold. The RFCs in `docs/rfcs/` define the intended
architecture; most implementation does not exist yet. Treat the RFCs as the
source of truth for design decisions and build toward them.

- `docs/rfcs/0001-project-scope.md` — scope, goals, non-goals, milestones
- `docs/rfcs/0002-architecture.md` — components, boundaries, project layout
- `docs/rfcs/0003-document-ingestion.md` — ingestion pipeline and data model
- `docs/rfcs/0004-rag-pipeline.md` — retrieval, context, prompting, grounding
- `docs/rfcs/0005-api.md` — HTTP endpoints, schemas, error format
- `docs/rfcs/0006-testing-and-evaluation.md` — test strategy and RAG evaluation

## Guiding Principle

> Build the smallest useful RAG system first.

Do not add a feature unless it is required to prove the core workflow
(ingest → index → ask → retrieve → answer → cite sources). Consult the
non-goals in RFC 0001 and the deferred items in each RFC before proposing
new abstractions or dependencies.

## Tech Stack

| Area | Choice |
|---|---|
| Language | Python 3.14+ |
| Package manager | `uv` |
| API | FastAPI |
| Database | PostgreSQL + pgvector |
| Embeddings | Single provider |
| LLM | Single provider |
| Testing | pytest |

The declared minimum is Python `>=3.14` (`pyproject.toml`, `.python-version`).
Use modern typing syntax (PEP 604 unions, built-in generics).

## Commands

```bash
uv run pytest                          # run tests
uv run <script>                        # run any Python entry point
uv add <package>                       # add a runtime dependency
uv add --dev <package>                 # add a dev dependency
uv sync                                # sync the environment
```

Always use `uv`. Do not invoke `pip` or bare `python` directly.

## Project Structure

RFC 0002 specifies the target layout. The installed package lives under
`src/up_vault/` (see `pyproject.toml`); the RFC shows an `app/` tree that maps
onto this package.

```text
src/up_vault/
├── api/            # FastAPI routes, request/response schemas
├── ingestion/      # validation, extraction, chunking, embedding, persistence
├── retrieval/      # query embedding, vector search, context construction
├── llm/            # prompt construction, provider client, answer generation
├── models/         # domain and persistence models
├── config.py       # settings
└── main.py         # application entry point
tests/
docs/rfcs/
```

## Architecture Rules

- **Keep business logic independent of HTTP.** Ingestion and RAG services must
  be usable without going through FastAPI.
- **API layer stays thin.** It validates requests, calls application services,
  and serializes responses. No RAG or ingestion logic in route handlers.
- **Keep providers replaceable.** Access LLM and embedding providers through
  small interfaces where practical.
- **Avoid premature abstraction.** Do not introduce interfaces or
  abstractions solely for hypothetical future providers.
- **The LLM never retrieves documents.** Retrieval is a separate, upstream step.
- **Retrieved context is the source of truth.** Answers must be grounded;
  refuse with an explicit "insufficient information" response when context is
  inadequate. If no relevant chunks are found, do not call the LLM.

## Domain Conventions

- Supported formats in the MVP: Markdown (`.md`) and plain text (`.txt`).
  PDF, HTML, DOCX, and OCR are explicitly out of scope.
- Chunking is deterministic fixed-size with a small overlap. Preserve chunk
  order and document identity. Each chunk carries `document_id`,
  `chunk_index`, and `filename` metadata.
- Ingestion is all-or-nothing: on embedding or persistence failure, the
  operation fails and leaves no partial data.
- Deleting a document cascades to its chunks and embeddings, enforced at the
  database level.
- `top_k` retrieval defaults to a small value (e.g. `5`) and is configurable.
- Use the same embedding model for documents and queries so vectors share one
  space.
- Deferred for the MVP: hybrid search, reranking, query expansion, multi-query
  retrieval, agentic retrieval, semantic chunking, and incremental re-indexing.

## API Conventions

Endpoints: `POST /documents`, `GET /documents`,
`DELETE /documents/{document_id}` (returns `204`), `POST /query`.

Errors use a consistent envelope:

```json
{ "error": { "code": "DOCUMENT_NOT_FOUND", "message": "Document was not found." } }
```

Common codes: `INVALID_DOCUMENT`, `UNSUPPORTED_FILE_TYPE`, `DOCUMENT_NOT_FOUND`,
`INGESTION_FAILED`, `RETRIEVAL_FAILED`, `LLM_ERROR`.

The `POST /query` response returns both `answer` and `sources` (with
`document_id`, `filename`, `chunk_index`). Authentication is out of scope for
the local MVP.

## Testing

- Use pytest. Run with `uv run pytest`.
- Prioritize confidence in the core ingestion and retrieval pipeline over raw
  coverage.
- Unit tests: file validation, text extraction, empty documents, chunking and
  chunk ordering, metadata generation, query embedding, top-K retrieval,
  similarity filtering, no-result behavior, request validation, response
  schemas, and error responses.
- Integration test: the full upload → extract → chunk → embed → store → query →
  retrieve → generate path.
- Maintain a small fixed RAG evaluation dataset covering direct questions,
  multi-chunk questions, and questions with no answer in the knowledge base.
  Verify the expected source appears in retrieved results, and that the system
  refuses appropriately when context is insufficient.
- Add known failures as regression cases; retrieval or prompt changes must not
  silently degrade previously working questions.

## Code Style

- Match the existing style and keep changes minimal and focused.
- Prefer clear, typed function signatures; annotate public functions.
- Keep modules cohesive with the layer boundaries above.
- Update the relevant RFC when a design decision changes, rather than leaving
  docs and code out of sync.
