# Implementation TODO

Outstanding work derived from the RFCs in `docs/rfcs/`. Only features the RFCs
actually require are listed — see "Out of scope" before adding anything new.

- Source of truth: RFC 0001–0006.
- Last reviewed: 2026-10-26 (`feat/query-endpoint`).
- Delete an item once it lands, so this file never lists finished work.

## Ingestion over HTTP (RFC 0001 M2, RFC 0005 §3)

- [ ] `POST /documents` — multipart upload, returns `{id, filename, status}`.
- [ ] Validate the file type (`.md`, `.txt` only) and return
      `UNSUPPORTED_FILE_TYPE` for anything else (RFC 0003 §4).
- [ ] Reject empty documents with `INVALID_DOCUMENT` (RFC 0003 §4).
- [ ] Enforce a maximum file size before processing (RFC 0003 §4).
- [ ] Return `INGESTION_FAILED` when embedding or persistence fails, and leave
      no partial data behind (RFC 0003 §11).
- [ ] Pick the loader by source format instead of always using `TextLoader`
      (RFC 0003 §5) — only needed once a second format exists.

## Ingestion service (RFC 0003)

- [ ] Persist `filename` in chunk metadata alongside `document_id` and
      `chunk_index` (RFC 0003 §7). Today `metadata_` is never populated and the
      filename is only reachable through the `document` relationship.
- [ ] Re-index a document by replacing its chunks (RFC 0003 §10).

## Documents API (RFC 0005 §4–§5)

- [ ] `GET /documents` — list indexed documents with `id`, `filename`,
      `created_at`.
- [ ] `DELETE /documents/{document_id}` — `204`, cascading to chunks and
      embeddings (cascade already enforced at the database level).
- [ ] `DOCUMENT_NOT_FOUND` for unknown document ids.

## RAG — generation (RFC 0002 §3, RFC 0004 §5–§9)

- [ ] Add an LLM provider interface plus a single implementation, behind
      settings like the embedding provider (`config.py` has no LLM settings).
- [ ] Build the context string, labelling each chunk
      `[Source: <filename>, chunk <index>]` (RFC 0004 §5).
- [ ] Prompt the model to answer only from context, to avoid unsupported
      claims, and to state when context is insufficient (RFC 0004 §6–§7).
- [ ] Return `answer` from `POST /query` next to `sources` (RFC 0004 §8,
      RFC 0005 §6).
- [ ] Do not call the LLM when retrieval returns no chunks; return an explicit
      insufficient-information response (RFC 0004 §9). Today `/query` returns
      `{"sources": []}`.
- [ ] Map provider failures to `LLM_ERROR` (RFC 0005 §7).

## Retrieval (RFC 0004 §4, RFC 0006 §2)

- [ ] Apply a similarity threshold so weak matches are not offered as context
      ("similarity filtering" is still untested and unimplemented).
- [ ] Make the default `top_k` configurable in `config.py`; it is currently a
      literal `5` in the request schema.
- [ ] Surface `RETRIEVAL_FAILED` when the vector search itself fails.

## API conventions (RFC 0005 §7)

- [ ] Error envelope `{"error": {"code": ..., "message": ...}}` via exception
      handlers — no endpoint currently emits it.
- [ ] Consistent status codes for the errors above.

## Testing and evaluation (RFC 0006)

- [ ] Unit tests for file validation, text extraction, and empty documents
      (blocked on the ingestion validation above).
- [ ] Unit test for similarity filtering and for the insufficient-context path.
- [ ] Tests for error responses once the envelope exists.
- [ ] One end-to-end integration test through HTTP:
      upload → extract → chunk → embed → store → query → retrieve → generate →
      cite sources (RFC 0006 §3).
- [ ] Fixed RAG evaluation dataset covering direct questions, multi-chunk
      questions, and questions with no answer in the knowledge base
      (RFC 0006 §4).
- [ ] Retrieval evaluation harness asserting the expected source appears in the
      top-k results (RFC 0006 §5).
- [ ] Grounding checks: refusal on insufficient context and correct source
      attribution (RFC 0006 §6).
- [ ] Regression cases for known failures (RFC 0006 §7).

## Documentation and housekeeping

- [ ] `README.md` is empty — write local setup instructions (install, `.env`,
      `make create-db`, `make migrate`, `make run`, `make test`) (RFC 0001 M4).
- [ ] Remove `cli/` once ingestion and query are both reachable over HTTP
      (RFC 0002 §9). Until then it stays the only way to ingest.
- [ ] Dev database is one revision behind (`alembic current` reports
      `6bb2433cb5c9`, head is `df58997075ce`) — run `make check-migration`.

## Reference: what exists today

Not a checklist — just orientation, so nothing above gets built twice.

- `POST /query`: embeds the question, returns ranked `sources`
  (`document_id`, `filename`, `chunk_index`). No `answer`, no threshold.
- Ingestion service: `TextLoader` → fixed-size chunking with overlap →
  embeddings → all-or-nothing persistence.
- `cli/ingest.py`: `up-vault ingest file <path>`.
- PostgreSQL + pgvector with `documents` and `chunks`
  (`chunks.document_id` cascades on delete).
- Embedding providers: `dummy` and `infinity`, selected by settings.
- Tests: chunking, retrieval (unit + database), cascade, embeddings, health,
  `/query` route.

## Out of scope for the MVP

Do not add these without changing RFC 0001/0004 first: autonomous agents, tool
calling, web search, voice, image understanding, OCR, knowledge graphs, memory
systems, fine-tuning, multi-agent workflows, extra vector databases,
authentication/multi-tenancy, distributed job processing, PDF/HTML/DOCX/web
loaders, hybrid search, reranking, query expansion, multi-query retrieval,
agentic retrieval, semantic chunking, incremental re-indexing.
