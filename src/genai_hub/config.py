from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "GenAI Integration Hub"
    debug: bool = False
    api_key: str = "demo-api-key-change-in-production"

    jwt_secret: str = "change-me-to-a-random-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    default_llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-haiku-latest"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:0.5b"

    pii_redaction_enabled: bool = True
    allowed_data_regions: str = "EU,CH"


@lru_cache
def get_settings() -> Settings:
    return Settings()
