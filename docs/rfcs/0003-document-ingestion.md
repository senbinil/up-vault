# RFC 0003: Document Ingestion

- **Status:** Draft
- **Date:** 2026-10-05
- **Depends on:** RFC 0001, RFC 0002

## 1. Summary

This RFC defines how documents are imported into up-vault and converted into searchable chunks.

## 2. Supported Formats

The MVP supports:

- Markdown (`.md`)
- Plain text (`.txt`)

PDF and other formats are explicitly deferred.

## 3. Ingestion Pipeline

```text
File
 ↓
Validation
 ↓
Text Extraction
 ↓
Normalization
 ↓
Chunking
 ↓
Embedding Generation
 ↓
Persistence
```

## 4. Validation

The API must validate:

- Supported file type.
- Non-empty content.
- Maximum file size.

Invalid documents must be rejected before processing.

## 5. Text Extraction

The extraction layer converts a supported document into plain text.

The rest of the ingestion pipeline should not depend on the original file format.

## 6. Chunking

The MVP uses deterministic fixed-size chunking with overlap.

Requirements:

- Consistent chunk size.
- Small overlap.
- Preserve chunk order.
- Preserve document identity.

Semantic chunking is deferred.

## 7. Metadata

Each chunk must retain:

```json
{
  "document_id": "uuid",
  "chunk_index": 0,
  "filename": "notes.md"
}
```

Additional metadata may be added when required for source attribution.

## 8. Persistence

A document and its chunks are stored separately.

```text
Document
├── id
├── filename
├── content_type
└── created_at

DocumentChunk
├── id
├── document_id
├── content
├── chunk_index
├── embedding
└── created_at
```

## 9. Deletion

Deleting a document must delete all associated chunks and embeddings.

The database relationship should enforce this behavior.

## 10. Re-indexing

The MVP may re-index a document by deleting its existing chunks and creating new ones.

Incremental chunk-level updates are deferred.

## 11. Failure Handling

If embedding or persistence fails:

- The ingestion operation must fail.
- Partial data should not remain.
- The error should be reported to the caller.

## 12. Future Work

Possible future formats:

- PDF
- HTML
- DOCX
- Web pages

These are outside the MVP.