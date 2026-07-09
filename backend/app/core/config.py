import json
import logging
from typing import List

from pydantic_settings import BaseSettings
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    PROJECT_NAME: str = "StadiumAI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000"]'

    @property
    def cors_origins(self) -> List[str]:
        v = self.BACKEND_CORS_ORIGINS.strip().strip("'\"")
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    DATABASE_URL: str = "sqlite:///./stadiumai.db"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = ""

    REDIS_URL: str = "redis://localhost:6379"

    LIMITER: Limiter = Limiter(key_func=get_remote_address)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
