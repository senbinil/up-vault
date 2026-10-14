from up_vault.services.embeddings.base import EmbeddingProvider


class DummyEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 1536) -> None:
        self.dimension = dimension

    async def embed(self, text: str) -> list[float]:
        return [0.0] * self.dimension
