# RFC 0004: RAG Pipeline

- **Status:** Draft
- **Date:** 2026-10-05
- **Depends on:** RFC 0002, RFC 0003

## 1. Summary

This RFC defines how up-vault retrieves relevant knowledge and generates grounded answers.

## 2. Query Flow

```text
User Question
      ↓
Query Embedding
      ↓
Vector Search
      ↓
Top-K Chunks
      ↓
Context Construction
      ↓
LLM
      ↓
Answer + Sources
```

## 3. Query Embedding

The same embedding model used for document chunks should be used for query embeddings.

This ensures that document and query vectors exist in the same vector space.

## 4. Retrieval

The MVP uses vector similarity search against document chunks.

The initial retrieval configuration should use a small `top_k`, such as:

```text
top_k = 5
```

The value should be configurable.

## 5. Context Construction

Retrieved chunks are assembled into a context supplied to the LLM.

Each chunk should retain its source metadata.

Example:

```text
[Source: architecture.md, chunk 3]

PostgreSQL is used as the primary database...
```

## 6. Prompt

The LLM should be instructed to:

1. Answer using the supplied context.
2. Avoid unsupported claims.
3. State when the context is insufficient.
4. Provide source references.

Conceptually:

```text
You are a personal knowledge assistant.

Answer the user's question using only the provided context.

If the context does not contain enough information,
say that you do not have enough information.

Context:
{context}

Question:
{question}
```

## 7. Grounding

The assistant must not treat retrieved context as optional background.

The retrieved context is the source of truth for the answer.

If relevant information cannot be found, the system should prefer:

```text
I don't have enough information in the available documents.
```

over generating an unsupported answer.

## 8. Sources

The response must identify the documents used to answer the question.

Example:

```json
{
  "answer": "The application uses PostgreSQL.",
  "sources": [
    {
      "document_id": "123",
      "filename": "architecture.md",
      "chunk_index": 3
    }
  ]
}
```

## 9. Retrieval Failure

If no relevant chunks are found, the LLM should not be called.

The API should return an insufficient-context response.

## 10. Initial Retrieval Strategy

The MVP intentionally excludes:

- Hybrid search.
- Reranking.
- Query expansion.
- Multi-query retrieval.
- Agentic retrieval.

These can be evaluated after establishing a baseline.

## 11. Future Improvements

Potential improvements:

- Hybrid keyword + vector search.
- Reranking.
- Query rewriting.
- Semantic chunking.
- Retrieval evaluation.
- Conversation-aware retrieval.