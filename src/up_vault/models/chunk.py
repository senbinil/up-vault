from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from up_vault.models.base import Base
from up_vault.models.document import Document

# Must match the configured embedding model. See
# EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 (384 dimensions).
EMBEDDING_DIMENSION = 384


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE")
    )
    content: Mapped[str]
    chunk_index: Mapped[int]
    token_count: Mapped[int | None]

    metadata_: Mapped[dict] = mapped_column(JSONB, default=dict)

    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSION))

    # `raise` keeps async code from triggering a lazy load outside the
    # retrieval query, which would fail with MissingGreenlet.
    document: Mapped[Document] = relationship(lazy="raise")
