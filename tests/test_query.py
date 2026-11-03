from collections.abc import AsyncIterator

import httpx
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from up_vault.api.routes import query as query_route
from up_vault.database import SessionLocal
from up_vault.main import app
from up_vault.models.chunk import EMBEDDING_DIMENSION, Chunk
from up_vault.models.document import Document
from up_vault.services.embeddings.base import EmbeddingProvider

client = TestClient(app)

CLOSEST_VECTOR = [1.0] + [0.0] * (EMBEDDING_DIMENSION - 1)
OTHER_VECTOR = [0.0, 1.0] + [0.0] * (EMBEDDING_DIMENSION - 2)


class FixedEmbeddingProvider(EmbeddingProvider):
    """Stub provider so route tests never reach a real embedding service."""

    def __init__(self, embedding: list[float]) -> None:
        self.embedding = embedding
        self.closed = False

    async def embed(self, text: str) -> list[float]:
        return self.embedding

    async def aclose(self) -> None:
        self.closed = True


async def _clear_documents() -> None:
    # The test database is dedicated to tests. Clearing documents keeps
    # retrieval assertions deterministic; chunks cascade at the database level.
    async with SessionLocal() as session:
        await session.execute(delete(Document))
        await session.commit()


@pytest.fixture
async def empty_knowledge_base() -> AsyncIterator[None]:
    await _clear_documents()
    try:
        yield
    finally:
        await _clear_documents()


def _use_provider(monkeypatch: pytest.MonkeyPatch, provider: EmbeddingProvider) -> None:
    monkeypatch.setattr(query_route, "create_embedding_provider", lambda: provider)


async def _post_query(payload: dict[str, object]) -> httpx.Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        return await async_client.post("/query", json=payload)


def test_query_rejects_empty_question():
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422


def test_query_rejects_invalid_limit():
    response = client.post("/query", json={"question": "something", "limit": 101})
    assert response.status_code == 422


def test_query_rejects_missing_question():
    response = client.post("/query", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_query_returns_sources_ranked_by_similarity(
    empty_knowledge_base: None, monkeypatch: pytest.MonkeyPatch
):
    provider = FixedEmbeddingProvider(CLOSEST_VECTOR)
    _use_provider(monkeypatch, provider)

    async with SessionLocal() as session:
        document = Document(
            filename="guide.md",
            source_type="text",
            content_hash="query-endpoint-test",
        )
        session.add(document)
        await session.flush()

        session.add_all(
            [
                Chunk(
                    document_id=document.id,
                    content="Reset your password from settings.",
                    chunk_index=0,
                    token_count=6,
                    embedding=CLOSEST_VECTOR,
                ),
                Chunk(
                    document_id=document.id,
                    content="Unrelated content.",
                    chunk_index=1,
                    token_count=2,
                    embedding=OTHER_VECTOR,
                ),
            ]
        )
        await session.commit()
        document_id = document.id

    response = await _post_query({"question": "how do I reset my password?"})

    assert response.status_code == 200
    assert response.json() == {
        "sources": [
            {
                "document_id": document_id,
                "filename": "guide.md",
                "chunk_index": 0,
            },
            {
                "document_id": document_id,
                "filename": "guide.md",
                "chunk_index": 1,
            },
        ]
    }
    assert provider.closed is True


@pytest.mark.asyncio
async def test_query_respects_limit(
    empty_knowledge_base: None, monkeypatch: pytest.MonkeyPatch
):
    provider = FixedEmbeddingProvider(CLOSEST_VECTOR)
    _use_provider(monkeypatch, provider)

    async with SessionLocal() as session:
        document = Document(
            filename="guide.md",
            source_type="text",
            content_hash="query-limit-test",
        )
        session.add(document)
        await session.flush()

        session.add_all(
            [
                Chunk(
                    document_id=document.id,
                    content="Closest content.",
                    chunk_index=0,
                    token_count=2,
                    embedding=CLOSEST_VECTOR,
                ),
                Chunk(
                    document_id=document.id,
                    content="Farther content.",
                    chunk_index=1,
                    token_count=2,
                    embedding=OTHER_VECTOR,
                ),
            ]
        )
        await session.commit()
        document_id = document.id

    response = await _post_query({"question": "reset", "limit": 1})

    assert response.status_code == 200
    assert response.json() == {
        "sources": [
            {
                "document_id": document_id,
                "filename": "guide.md",
                "chunk_index": 0,
            }
        ]
    }


@pytest.mark.asyncio
async def test_query_returns_no_sources_when_knowledge_base_is_empty(
    empty_knowledge_base: None, monkeypatch: pytest.MonkeyPatch
):
    provider = FixedEmbeddingProvider(CLOSEST_VECTOR)
    _use_provider(monkeypatch, provider)

    response = await _post_query({"question": "anything at all"})

    assert response.status_code == 200
    assert response.json() == {"sources": []}
    assert provider.closed is True
