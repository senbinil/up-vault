from up_vault.models.chunk import EMBEDDING_DIMENSION
from up_vault.services.embeddings.base import EmbeddingProvider


class DummyEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = EMBEDDING_DIMENSION) -> None:
        self.dimension = dimension

    async def embed(self, text: str) -> list[float]:
        return [0.0] * self.dimension
