"""TailorResume — Application Configuration"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tailorresume"
    
    # JWT Auth
    JWT_SECRET: str = "change-this-secret-key"
    JWT_EXPIRY_HOURS: int = 72
    JWT_ALGORITHM: str = "HS256"
    
    # LLM Configuration (customizable)
    LLM_PROVIDER: str = "openai"  # openai | anthropic | gemini | deepseek | ollama
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_BASE_URL: Optional[str] = None
    
    # Separate LLM for content generation (optional)
    LLM_CONTENT_PROVIDER: Optional[str] = None
    LLM_CONTENT_API_KEY: Optional[str] = None
    LLM_CONTENT_MODEL: Optional[str] = None
    LLM_CONTENT_BASE_URL: Optional[str] = None
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","chrome-extension://ajgnfmojakmcoicgnmnfefiliaeikmah"]'
    
    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    @property
    def cors_origins_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:3000"]
    
    @property
    def content_provider(self) -> str:
        return self.LLM_CONTENT_PROVIDER or self.LLM_PROVIDER
    
    @property
    def content_api_key(self) -> str:
        return self.LLM_CONTENT_API_KEY or self.LLM_API_KEY
    
    @property
    def content_model(self) -> str:
        return self.LLM_CONTENT_MODEL or self.LLM_MODEL
    
    @property
    def content_base_url(self) -> Optional[str]:
        return self.LLM_CONTENT_BASE_URL or self.LLM_BASE_URL
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
