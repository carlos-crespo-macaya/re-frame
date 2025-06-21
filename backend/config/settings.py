"""Configuration settings for re-frame backend."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_title: str = "re-frame API"
    api_version: str = "0.1.0"
    api_description: str = "AI-assisted cognitive reframing support tool for AvPD"
    
    # Google AI Configuration
    google_ai_api_key: str
    google_ai_model: str = "gemini-1.5-flash"
    google_ai_temperature: float = 0.7
    google_ai_max_tokens: int = 2048
    
    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:3000", "https://re-frame.social"]
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_period: int = 3600  # 1 hour in seconds
    
    # Logging
    log_level: str = "INFO"
    
    # Security
    content_filter_threshold: float = 0.8
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()