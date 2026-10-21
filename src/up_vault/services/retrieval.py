from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from up_vault.models.chunk import Chunk
from up_vault.services.embeddings.base import EmbeddingProvider


class RetrievalService:
    def __init__(
        self, session: AsyncSession, embedding_provider: EmbeddingProvider
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider

    async def search(self, query: str, limit: int = 5) -> list[Chunk]:
        query_embedding = await self.embedding_provider.embed(query)

        statement = (
            select(Chunk)
            .order_by(Chunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await self.session.scalars(statement)
        return list(result.all())
