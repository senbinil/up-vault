import pytest
from pydantic import ValidationError

from up_vault.config import Settings, settings
from up_vault.services.embeddings import factory
from up_vault.services.embeddings.dummy import DummyEmbeddingProvider
from up_vault.services.embeddings.infinity import InfinityEmbeddingProvider


def test_settings_read_embedding_configuration_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EMBEDDING_PROVIDER", "dummy")
    monkeypatch.setenv("EMBEDDING_MODEL", "custom-model")
    monkeypatch.setenv("EMBEDDING_BASE_URL", "http://from-env:1234")
    monkeypatch.setenv("EMBEDDING_TIMEOUT_SECONDS", "5")

    loaded = Settings()

    assert loaded.embedding_provider == "dummy"
    assert loaded.embedding_model == "custom-model"
    assert loaded.embedding_base_url == "http://from-env:1234"
    assert loaded.embedding_timeout_seconds == 5.0


def test_settings_reject_unsupported_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")

    with pytest.raises(ValidationError):
        Settings()


def test_factory_creates_dummy_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "embedding_provider", "dummy")

    provider = factory.create_embedding_provider()

    assert isinstance(provider, DummyEmbeddingProvider)


def test_factory_creates_infinity_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "embedding_provider", "infinity")
    monkeypatch.setattr(settings, "embedding_model", "test-model")
    monkeypatch.setattr(settings, "embedding_base_url", "http://infinity.test")
    monkeypatch.setattr(settings, "embedding_timeout_seconds", 5.0)

    provider = factory.create_embedding_provider()

    assert isinstance(provider, InfinityEmbeddingProvider)
    assert provider.model == "test-model"
    assert provider.base_url == "http://infinity.test"
    assert provider.timeout == 5.0
