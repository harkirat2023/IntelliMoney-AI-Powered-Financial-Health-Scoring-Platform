from functools import lru_cache
from typing import Annotated

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import NoDecode


class ProcessingSettings(BaseSettings):
    max_batch_size: int = 500
    max_retries: int = 3
    stage_timeout_seconds: int = 30
    confidence_threshold: float = 0.7
    force_processing: bool = False
    alert_cooldown_hours: int = 1


class Settings(BaseSettings):
    app_name: str = "IntelliMoney"
    version: str = "1.0.0"
    environment: str = "development"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "intellimoney"
    redis_url: str = ""
    log_level: str = "INFO"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:80", "http://localhost"],
    )

    bank_encryption_key: str
    bank_consent_redirect_base: str = "http://localhost:5173/connect-bank/consent"

    processing: ProcessingSettings = ProcessingSettings()

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.3
    openai_max_tokens: int = 1024
    openai_embedding_model: str = "text-embedding-3-small"
    upload_dir: str = "uploads/receipts"

    supabase_url: str = ""
    supabase_service_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="before")
    @classmethod
    def parse_cors_origins(cls, data: dict) -> dict:
        origins = data.get("cors_origins")
        if isinstance(origins, str):
            data["cors_origins"] = [o.strip() for o in origins.split(",") if o.strip()]
        return data


@lru_cache
def get_settings() -> Settings:
    return Settings()
