import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("ENV", "development")

ENV_FILES = {
    "development": ".env.development",
    "test": ".env.test",
}

if ENV not in ENV_FILES:
    supported = ", ".join(sorted(ENV_FILES))
    raise ValueError(f"Unknown ENV {ENV!r}; expected one of: {supported}.")

env_file = ENV_FILES[ENV]


class Settings(BaseSettings):
    database_url: str = ""
    database_admin_url: str = ""
    embedding_provider: Literal["dummy", "infinity"] = "dummy"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_base_url: str = "http://localhost:7997"
    embedding_timeout_seconds: float = 30.0
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")


settings = Settings()
