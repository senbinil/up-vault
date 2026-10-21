from up_vault.config import settings
from up_vault.services.embeddings.base import EmbeddingProvider
from up_vault.services.embeddings.dummy import DummyEmbeddingProvider
from up_vault.services.embeddings.infinity import InfinityEmbeddingProvider


def create_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider == "dummy":
        return DummyEmbeddingProvider()

    return InfinityEmbeddingProvider(
        base_url=settings.embedding_base_url,
        model=settings.embedding_model,
        timeout=settings.embedding_timeout_seconds,
    )
