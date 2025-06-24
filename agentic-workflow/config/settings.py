"""Configuration settings for re-frame backend."""

import base64
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App Configuration
    app_name: str = "state_app"

    # API Configuration
    api_title: str = "re-frame API"
    api_version: str = "0.1.0"
    api_description: str = "AI-assisted cognitive reframing support tool for AvPD"

    # Google AI Configuration
    google_ai_api_key: str = Field(default="", alias="GOOGLE_API_KEY")  # Maps from Doppler env var
    google_ai_model: str = "gemini-1.5-flash"
    google_ai_temperature: float = 0.7
    google_ai_max_tokens: int = 2048

    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:3000", "https://re-frame.social"]

    # Rate Limiting (using in-memory storage for now)
    # TODO: For production deployment, integrate Redis for distributed rate limiting
    rate_limit_requests: int = 10
    rate_limit_period: int = 3600  # 1 hour in seconds

    # Redis Configuration (for future distributed rate limiting)
    # redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    # redis_password: str | None = Field(default=None, alias="REDIS_PASSWORD")

    # Logging
    log_level: str = "INFO"

    # Security & Abuse Prevention
    content_filter_threshold: float = 0.8
    enable_perspective_api: bool = False
    perspective_api_key: str | None = Field(default=None, alias="PERSPECTIVE_API_KEY")
    toxicity_threshold: float = 0.7

    # Supabase Configuration
    supabase_connection_string: str = Field(default="", alias="SUPABASE_CONNECTION_STRING")

    # Langfuse Configuration
    langfuse_host: str = Field(default="", alias="LANGFUSE_HOST")
    langfuse_public_key: str = Field(default="", alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(default="", alias="LANGFUSE_SECRET_KEY")

    @property
    def langfuse_bearer_token(self) -> str:
        """Generate a bearer token for Langfuse."""
        return base64.b64encode(f"{self.langfuse_public_key}:{self.langfuse_secret_key}".encode()).decode()

    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        case_sensitive = False
        populate_by_name = True  # Allow both field name and alias


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
