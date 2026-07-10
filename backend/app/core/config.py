from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProcessingSettings(BaseSettings):
    max_batch_size: int = 500
    max_retries: int = 3
    stage_timeout_seconds: int = 30
    confidence_threshold: float = 0.7
    force_processing: bool = False
    alert_cooldown_hours: int = 1


class Settings(BaseSettings):
    app_name: str = "IntelliMoney"
    environment: str = "development"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "intellimoney"
    redis_url: str = ""
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:80", "http://localhost"]

    bank_encryption_key: str
    bank_consent_redirect_base: str = "http://localhost:5173/connect-bank/consent"

    processing: ProcessingSettings = ProcessingSettings()

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.3
    openai_max_tokens: int = 1024
    openai_embedding_model: str = "text-embedding-3-small"
    upload_dir: str = "uploads/receipts"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
