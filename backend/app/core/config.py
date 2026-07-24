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
    refresh_token_expire_minutes: int = 60 * 24 * 7
    rate_limit_auth_enabled: bool = True
    rate_limit_auth_max_requests: int = 10
    rate_limit_auth_window_seconds: int = 60
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "IntelliMoney"
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

    groq_api_key: str = ""
    groq_api_base: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama3-8b-8192"
    groq_temperature: float = 0.3
    groq_max_tokens: int = 1024
    upload_dir: str = "uploads/receipts"

    supabase_url: str = ""
    supabase_service_key: str = ""
    ml_allow_fallback: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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
