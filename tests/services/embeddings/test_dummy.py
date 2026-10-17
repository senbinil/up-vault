from up_vault.models.chunk import EMBEDDING_DIMENSION
from up_vault.services.embeddings.dummy import DummyEmbeddingProvider


async def test_embed_returns_a_vector_matching_the_schema_dimension() -> None:
    embedding = await DummyEmbeddingProvider().embed("hello")

    assert len(embedding) == EMBEDDING_DIMENSION


async def test_embed_batch_preserves_order_and_count() -> None:
    embeddings = await DummyEmbeddingProvider().embed_batch(["a", "b", "c"])

    assert len(embeddings) == 3
    assert all(len(embedding) == EMBEDDING_DIMENSION for embedding in embeddings)
