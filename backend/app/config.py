from functools import lru_cache
from pydantic import BaseSettings, AnyUrl, Field
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment.

    All values can be overridden via environment variables. For local
    development you can create a .env file (not committed) or use the
    workspace Secrets panel.
    """

    APP_NAME: str = "PSXviewAI API"
    APP_ENV: str = Field("development", description="Environment name")

    # Database
    DATABASE_URL: Optional[AnyUrl] = Field(
        default=None,
        description=(
            "SQLAlchemy database URL. In production this should point to "
            "PostgreSQL; in local dev you may use SQLite."
        ),
    )

    # JWT / auth
    JWT_SECRET_KEY: str = Field(
        "changeme-in-env",
        description="Secret key for signing JWT access and refresh tokens.",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    API_V1_PREFIX: str = "/api"

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
