import pytest
from sqlalchemy import select

from up_vault.database import SessionLocal
from up_vault.models.chunk import EMBEDDING_DIMENSION, Chunk
from up_vault.models.document import Document


@pytest.mark.asyncio
async def test_deleting_document_cascades_to_chunks():
    async with SessionLocal() as session:
        document = Document(
            filename="cascade-test.txt",
            source_type="text",
            content_hash="cascade-test-hash",
        )
        session.add(document)
        await session.flush()

        chunk = Chunk(
            document_id=document.id,
            content="Chunk to be deleted",
            chunk_index=0,
            token_count=4,
            embedding=[1.0] + [0.0] * (EMBEDDING_DIMENSION - 1),
        )
        session.add(chunk)
        await session.commit()

        document_id = document.id
        chunk_id = chunk.id

        await session.delete(document)
        await session.commit()

        remaining_document_id = await session.scalar(
            select(Document.id).where(Document.id == document_id)
        )
        remaining_chunk_id = await session.scalar(
            select(Chunk.id).where(Chunk.id == chunk_id)
        )

        assert remaining_document_id is None
        assert remaining_chunk_id is None
