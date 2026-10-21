"""Centralized configuration loaded from environment variables.

Uses python-dotenv to optionally read a local .env file in development.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load a .env file if present (development convenience); real secrets come from
# the environment in production.
load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip() not in {"0", "false", "False", "no", ""}


@dataclass(frozen=True)
class Config:
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_challenge_ttl_seconds: int
    jwt_session_ttl_seconds: int
    cookie_name: str
    cookie_secure: bool
    smtp_host: str
    smtp_port: int
    smtp_user: Optional[str]
    smtp_password: Optional[str]
    smtp_from: Optional[str]
    gemini_api_key: Optional[str]
    gemini_model: str


def _build_config() -> Config:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./psxviewai.db")

    jwt_secret = os.getenv("JWT_SECRET", "change_me_to_a_long_random_string")
    jwt_algorithm = "HS256"

    # 10 minutes for OTP challenges, 7 days for sessions by default.
    jwt_challenge_ttl_seconds = int(os.getenv("JWT_CHALLENGE_TTL", "600"))
    jwt_session_ttl_seconds = int(os.getenv("JWT_SESSION_TTL", str(7 * 24 * 60 * 60)))

    cookie_name = os.getenv("SESSION_COOKIE_NAME", "psx_session")
    cookie_secure = _get_bool("COOKIE_SECURE", False)

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER") or None
    smtp_password = os.getenv("SMTP_PASSWORD") or None
    smtp_from = os.getenv("SMTP_FROM") or None

    gemini_api_key = os.getenv("GEMINI_API_KEY") or None
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    return Config(
        database_url=database_url,
        jwt_secret=jwt_secret,
        jwt_algorithm=jwt_algorithm,
        jwt_challenge_ttl_seconds=jwt_challenge_ttl_seconds,
        jwt_session_ttl_seconds=jwt_session_ttl_seconds,
        cookie_name=cookie_name,
        cookie_secure=cookie_secure,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        smtp_from=smtp_from,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
    )


config = _build_config()
