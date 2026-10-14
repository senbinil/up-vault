# RFC 0002: up-vault Architecture

- **Status:** Draft
- **Date:** 2026-10-05
- **Depends on:** RFC 0001

## 1. Summary

This RFC defines the high-level architecture for up-vault.

The architecture prioritizes simplicity and clear boundaries over extensibility.

## 2. Architecture

```text
                    ┌──────────────┐
                    │    Client    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    └──────┬───────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      Document Ingestion             RAG Query
             │                           │
             ▼                           ▼
         Chunking                   Retrieval
             │                           │
             ▼                           │
        Embeddings                       │
             │                           │
             └──────────┐     ┌──────────┘
                        ▼     ▼
                   PostgreSQL
                    + pgvector
                        │
                        ▼
                       LLM
                        │
                        ▼
                 Answer + Sources
```

## 3. Components

### API

FastAPI exposes the application interface.

Responsibilities:

- Request validation.
- Authentication when introduced.
- Calling application services.
- Serializing responses.

The API layer should not contain RAG or ingestion logic.

### Ingestion

Responsible for converting documents into searchable chunks.

```text
Document
   ↓
Text extraction
   ↓
Chunking
   ↓
Embedding
   ↓
Persistence
```

### Retrieval

Responsible for finding relevant document chunks for a query.

```text
Query
  ↓
Embedding
  ↓
Vector similarity search
  ↓
Relevant chunks
```

### LLM

Responsible for generating an answer using the retrieved context.

The LLM should not be responsible for retrieving documents.

### PostgreSQL + pgvector

PostgreSQL stores:

- Documents.
- Document chunks.
- Embeddings.
- Required metadata.

pgvector provides vector similarity search.

## 4. Project Structure

```text
up-vault/
├── src/
│   └── up_vault/               # installed package
│       ├── api/                # FastAPI routes, request/response schemas
│       ├── cli/                # Typer entry points that drive services directly
│       ├── services/           # application services
│       │   ├── embeddings/     # embedding provider interface and implementations
│       │   └── loaders/        # text extraction by source format
│       ├── models/             # domain and persistence models
│       ├── config.py           # settings
│       ├── database.py         # engine and session factory
│       └── main.py             # FastAPI application entry point
├── alembic/                    # migrations
│   └── versions/
├── scripts/                    # one-off developer scripts
├── tests/
├── docs/
│   └── rfcs/
├── pyproject.toml
├── uv.lock
├── README.md
└── .env.example
```

## 5. Design Principles

### Keep business logic independent of HTTP

RAG and ingestion services should be usable without going through FastAPI.

### Keep providers replaceable

LLM and embedding providers should be accessed through small interfaces where practical.

### Avoid premature abstraction

Do not introduce interfaces or abstractions solely for hypothetical future providers.

## 6. Data Flow

### Ingestion

```text
API
 ↓
Ingestion Service
 ↓
Text Extraction
 ↓
Chunking
 ↓
Embedding Provider
 ↓
PostgreSQL
```

### Query

```text
API
 ↓
RAG Service
 ↓
Embedding Provider
 ↓
PostgreSQL / pgvector
 ↓
Context Builder
 ↓
LLM
 ↓
API Response
```

## 7. Deployment

The MVP should run as a small application consisting of:

- up-vault application
- PostgreSQL + pgvector

No Kubernetes, message broker, or separate vector database is required.

## 8. Decision

The MVP will use PostgreSQL + pgvector rather than introducing a dedicated vector database.

## 9. Decision: Package Layout

The implementation package lives under `src/up_vault/` rather than a top-level
`app/` directory, so that it is importable as an installed package and resolves
consistently under `uv run`, pytest, and Alembic.

Ingestion, retrieval, and generation logic lives under `services/` rather than
the previously sketched top-level `ingestion/`, `retrieval/`, and `llm/`
packages. Two reasons:

- The layers share a uniform shape — validate, transform, call a provider,
  persist — so one `services/` package with format-specific and provider-specific
  subpackages (`loaders/`, `embeddings/`) is simpler than three parallel trees.
- It keeps the "keep providers replaceable" principle (section 5) local to where
  the adapters are consumed.

`cli/` holds commands that drive services directly without HTTP. It is
temporary scaffolding, used to exercise the ingestion and retrieval services
from tests while the API layer is still being built. It is not a supported
interface and is expected to be removed once `api/` covers the same ground.
`api/` holds the FastAPI layer and stays thin.