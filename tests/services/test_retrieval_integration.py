import pytest

from up_vault.database import SessionLocal
from up_vault.models.chunk import EMBEDDING_DIMENSION, Chunk
from up_vault.models.document import Document
from up_vault.services.embeddings.base import EmbeddingProvider
from up_vault.services.retrieval import RetrievalService


class FixedEmbeddingProvider(EmbeddingProvider):
    def __init__(self, embedding: list[float]) -> None:
        self.embedding = embedding

    async def embed(self, text: str) -> list[float]:
        return self.embedding


@pytest.mark.asyncio
async def test_search_ranks_closest_chunk_first():
    query_vector = [1.0] + [0.0] * (EMBEDDING_DIMENSION - 1)
    other_vector = [0.0, 1.0] + [0.0] * (EMBEDDING_DIMENSION - 2)
    opposite_vector = [-1.0] + [0.0] * (EMBEDDING_DIMENSION - 1)

    async with SessionLocal() as session:
        document = Document(
            filename="integration-test.txt",
            source_type="text",
            content_hash="integration-test-hash",
        )

        session.add(document)
        await session.flush()

        chunks = [
            Chunk(
                document_id=document.id,
                content="Closest",
                chunk_index=0,
                token_count=2,
                embedding=query_vector,
            ),
            Chunk(
                document_id=document.id,
                content="Unrelated",
                chunk_index=1,
                token_count=2,
                embedding=other_vector,
            ),
            Chunk(
                document_id=document.id,
                content="Opposite",
                chunk_index=2,
                token_count=2,
                embedding=opposite_vector,
            ),
        ]

        session.add_all(chunks)
        await session.commit()

        try:
            service = RetrievalService(session, FixedEmbeddingProvider(query_vector))
            results = await service.search("find the closest chunk", limit=2)

            assert [chunk.content for chunk in results] == [
                "Closest",
                "Unrelated",
            ]
        finally:
            for chunk in chunks:
                await session.delete(chunk)
            await session.delete(document)
            await session.commit()
