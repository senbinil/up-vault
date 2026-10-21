import httpx

from up_vault.services.embeddings.base import EmbeddingError, EmbeddingProvider


class InfinityEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by an Infinity server.

    Uses the OpenAI-compatible ``POST /embeddings`` endpoint. A single HTTP
    client is reused across calls and must be released with :meth:`aclose`.
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = client

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def embed(self, text: str) -> list[float]:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        try:
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                json={"model": self.model, "input": texts},
            )
            response.raise_for_status()
            return [item["embedding"] for item in response.json()["data"]]
        except httpx.HTTPStatusError as exc:
            raise EmbeddingError(
                f"Embedding request failed with status {exc.response.status_code}."
            ) from exc
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise EmbeddingError("Embedding request failed.") from exc
