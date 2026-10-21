"""Password hashing, signed tokens, OTP helpers."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import JWT_ALG, JWT_SECRET


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except ValueError:
        return False


def make_token(user_id: int, kind: str, minutes: int) -> str:
    """kind = 'challenge' (password OK, waiting for 2FA) or 'session' (fully logged in)."""
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "kind": kind, "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def read_token(token: str, kind: str) -> int | None:
    """Return the user id if the token is valid AND of the expected kind, else None."""
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.PyJWTError:
        return None
    if data.get("kind") != kind:
        return None
    try:
        return int(data["sub"])
    except (KeyError, ValueError):
        return None


def new_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(code: str) -> str:
    return hmac.new(JWT_SECRET.encode(), code.encode(), hashlib.sha256).hexdigest()


def same(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)