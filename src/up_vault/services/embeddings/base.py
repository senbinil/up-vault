from abc import ABC, abstractmethod


class EmbeddingError(Exception):
    """Raised when an embedding provider fails to produce embeddings."""


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        pass

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed several texts, preserving input order.

        Providers that support batching should override this to reduce the
        number of round trips.
        """
        return [await self.embed(text) for text in texts]

    async def aclose(self) -> None:
        """Release provider resources. No-op for providers without any."""
