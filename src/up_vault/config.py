from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = ""
    database_admin_url: str = ""
    embedding_provider: Literal["dummy", "infinity"] = "dummy"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_base_url: str = "http://localhost:7997"
    embedding_timeout_seconds: float = 30.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
