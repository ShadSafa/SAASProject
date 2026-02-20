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

    # Instagram OAuth
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    INSTAGRAM_REDIRECT_URI: str = "http://localhost:8000/integrations/instagram/callback"

    # Token encryption
    TOKEN_ENCRYPTION_KEY: str = ""  # Fernet key for encrypting access tokens; generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

    # Celery / Redis
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # AWS S3 for thumbnail caching
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_S3_REGION: str = "us-east-1"

    # Third-party scan APIs
    APIFY_API_KEY: str = ""
    PHANTOMBUSTER_API_KEY: str = ""
    PHANTOMBUSTER_AGENT_ID: str = ""

    # OpenAI API (required for viral analysis)
    OPENAI_API_KEY: str = ""

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields from .env (like NGROK_URL) without error


settings = Settings()
