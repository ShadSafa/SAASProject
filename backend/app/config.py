from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration using Pydantic Settings."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localhost/instagram_analyzer"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"  # Must be changed in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Email Service
    RESEND_API_KEY: str = ""  # Required for email functionality
    RESEND_DOMAIN: str = "yourdomain.com"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
