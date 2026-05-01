from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "BOQ AI SaaS"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    ALLOWED_ORIGINS: List[str] = ["*"]
    JWT_SECRET: str = "super-secret-boq-ai-token-2024"
    JWT_ALGORITHM: str = "HS256"
    OPENAI_API_KEY: Optional[str] = None
    FRONTEND_URL: str = "https://boq-ai-frontend-site.onrender.com"
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings(): return Settings()
settings = get_settings()
