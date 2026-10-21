"""Security helpers: password hashing, JWT handling, and OTP utilities."""
from __future__ import annotations

import datetime as dt
import secrets
from typing import Literal, Optional

import bcrypt
import jwt

from config import config

JwtKind = Literal["challenge", "session"]


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_token(sub: str, kind: JwtKind, ttl_seconds: int) -> str:
    now = dt.datetime.utcnow()
    payload = {
        "sub": sub,
        "kind": kind,
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(seconds=ttl_seconds)).timestamp()),
    }
    return jwt.encode(payload, config.jwt_secret, algorithm=config.jwt_algorithm)


def create_challenge_token(sub: str) -> str:
    return create_token(sub, "challenge", config.jwt_challenge_ttl_seconds)


def create_session_token(sub: str) -> str:
    return create_token(sub, "session", config.jwt_session_ttl_seconds)


def decode_token(token: str, expected_kind: Optional[JwtKind] = None) -> dict:
    payload = jwt.decode(token, config.jwt_secret, algorithms=[config.jwt_algorithm])
    if expected_kind and payload.get("kind") != expected_kind:
        raise jwt.InvalidTokenError("wrong token kind")
    return payload


def generate_otp_code() -> str:
    """Generate a 6-digit numeric OTP code as a string."""
    return f"{secrets.randbelow(1_000_000):06d}"
