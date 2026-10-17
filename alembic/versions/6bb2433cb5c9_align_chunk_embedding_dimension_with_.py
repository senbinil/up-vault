"""align chunk embedding dimension with bge-small

Revision ID: 6bb2433cb5c9
Revises: 4f05cf19fbb5
Create Date: 2026-10-17 12:03:04.227935

"""

from collections.abc import Sequence

import pgvector.sqlalchemy

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6bb2433cb5c9"
down_revision: str | Sequence[str] | None = "4f05cf19fbb5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema.

    Embeddings are model-specific: 1536-dimensional vectors cannot be
    converted to 384 dimensions. Chunks (and documents left without chunks)
    are removed; re-ingest the source documents afterwards.
    """
    op.execute("DELETE FROM chunks")
    op.execute("DELETE FROM documents WHERE id NOT IN (SELECT document_id FROM chunks)")
    op.alter_column(
        "chunks",
        "embedding",
        type_=pgvector.sqlalchemy.vector.VECTOR(dim=384),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM chunks")
    op.execute("DELETE FROM documents WHERE id NOT IN (SELECT document_id FROM chunks)")
    op.alter_column(
        "chunks",
        "embedding",
        type_=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
        existing_nullable=False,
    )
