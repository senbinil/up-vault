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
├── app/
│   ├── api/
│   ├── ingestion/
│   ├── retrieval/
│   ├── llm/
│   ├── models/
│   ├── config.py
│   └── main.py
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