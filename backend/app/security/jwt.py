from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt

from app.config import get_settings


settings = get_settings()


def create_token(subject: str | int, expires_delta: timedelta, extra_claims: Dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
