import json
from collections.abc import Callable

import httpx
import pytest

from up_vault.services.embeddings.base import EmbeddingError
from up_vault.services.embeddings.infinity import InfinityEmbeddingProvider


def make_provider(
    handler: Callable[[httpx.Request], httpx.Response],
) -> tuple[InfinityEmbeddingProvider, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(record))
    provider = InfinityEmbeddingProvider(
        base_url="http://infinity.test/",
        model="test-model",
        timeout=5.0,
        client=client,
    )
    return provider, requests


async def test_embed_posts_single_input_and_returns_vector() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"data": [{"index": 0, "embedding": [0.1, 0.2]}]}
        )

    provider, requests = make_provider(handler)
    try:
        vector = await provider.embed("hello")
    finally:
        await provider.aclose()

    assert vector == [0.1, 0.2]
    assert len(requests) == 1
    assert str(requests[0].url) == "http://infinity.test/embeddings"
    assert json.loads(requests[0].content) == {
        "model": "test-model",
        "input": ["hello"],
    }


async def test_embed_batch_uses_one_request_and_preserves_order() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 0, "embedding": [0.1]},
                    {"index": 1, "embedding": [0.2]},
                    {"index": 2, "embedding": [0.3]},
                ]
            },
        )

    provider, requests = make_provider(handler)
    try:
        vectors = await provider.embed_batch(["a", "b", "c"])
    finally:
        await provider.aclose()

    assert len(requests) == 1
    assert json.loads(requests[0].content)["input"] == ["a", "b", "c"]
    assert vectors == [[0.1], [0.2], [0.3]]


async def test_embed_batch_of_nothing_makes_no_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no request expected")

    provider, requests = make_provider(handler)
    try:
        vectors = await provider.embed_batch([])
    finally:
        await provider.aclose()

    assert vectors == []
    assert requests == []


async def test_http_error_is_wrapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "boom"})

    provider, _ = make_provider(handler)
    try:
        with pytest.raises(EmbeddingError):
            await provider.embed("hello")
    finally:
        await provider.aclose()


async def test_malformed_response_is_wrapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": True})

    provider, _ = make_provider(handler)
    try:
        with pytest.raises(EmbeddingError):
            await provider.embed("hello")
    finally:
        await provider.aclose()
