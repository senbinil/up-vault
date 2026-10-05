# RFC 0006: Testing and Evaluation

- **Status:** Draft
- **Date:** 2026-10-05
- **Depends on:** RFC 0001–0005

## 1. Summary

This RFC defines how up-vault will be tested and how RAG quality will be evaluated.

The goal is not maximum test coverage.

The goal is confidence that the core ingestion and retrieval pipeline works correctly.

## 2. Unit Tests

Unit tests should cover:

### Ingestion

- File validation.
- Text extraction.
- Empty documents.
- Chunking.
- Chunk ordering.
- Metadata generation.

### Retrieval

- Query embedding.
- Top-K retrieval.
- Similarity filtering.
- No-result behavior.

### API

- Request validation.
- Response schemas.
- Error responses.

## 3. Integration Tests

At minimum:

```text
Upload document
      ↓
Extract text
      ↓
Create chunks
      ↓
Store embeddings
      ↓
Query
      ↓
Retrieve chunks
      ↓
Generate response
```

The integration test should verify the complete pipeline.

## 4. RAG Evaluation

A small fixed evaluation dataset should be maintained.

Example:

```json
{
  "question": "What database does the project use?",
  "expected_answer": "PostgreSQL",
  "expected_source": "architecture.md"
}
```

The dataset should contain:

- Direct questions.
- Questions requiring information from multiple chunks.
- Questions with no answer in the knowledge base.

## 5. Retrieval Evaluation

The evaluation should verify whether the expected source appears in the retrieved results.

Example:

```text
Question
   ↓
Retrieve top 5
   ↓
Expected source present?
```

This provides a basic retrieval-quality signal before evaluating generated answers.

## 6. Grounding Evaluation

Answers should be checked for:

- Correctness.
- Support from retrieved context.
- Source attribution.
- Appropriate refusal when context is insufficient.

## 7. Regression Tests

Known failures should be added to the evaluation dataset.

A retrieval or prompt change should not silently degrade previously working questions.

## 8. Test Commands

The project should expose simple commands through `uv`.

Example:

```bash
uv run pytest
```

## 9. MVP Quality Bar

The MVP should not be considered complete if:

- Documents cannot reliably be indexed.
- Relevant documents are consistently not retrieved.
- Answers regularly contain unsupported information.
- Sources cannot be traced back to documents.

## 10. Future Evaluation

Future versions may introduce:

- Automated RAG evaluation.
- Retrieval precision/recall.
- Faithfulness scoring.
- Answer relevance scoring.
- Larger benchmark datasets.

These are not required for the MVP.