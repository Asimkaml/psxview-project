from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import RefreshToken, User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate
from app.security.password import hash_password, verify_password
from app.security.jwt import create_token


settings = get_settings()


class AuthService:
    """User registration, login and session issuing.

    This mirrors the security model of the NestJS Auth & Accounts kit:
    - Short-lived stateless access tokens.
    - Long-lived refresh tokens stored **hashed** and rotated on use.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: UserCreate) -> tuple[User, str, str]:
        email = data.email.strip().lower()
        username = data.username.strip().lower()

        if self.users.get_by_email(email) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists",
            )
        if self.users.get_by_username(username) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this username already exists",
            )

        password_hash = hash_password(data.password)
        user = self.users.create(
            email=email,
            username=username,
            display_name=data.display_name or data.username,
            password_hash=password_hash,
        )

        access_token, refresh_token = self._issue_tokens(user)
        return user, access_token, refresh_token

    def login(self, *, email: str, password: str) -> tuple[User, str, str]:
        normalized_email = email.strip().lower()
        user = self.users.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.password_hash):
            # Constant error message to avoid account enumeration.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token, refresh_token = self._issue_tokens(user)
        return user, access_token, refresh_token

    def _issue_tokens(self, user: User) -> tuple[str, str]:
        now = datetime.now(timezone.utc)

        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = create_token(
            subject=user.id,
            expires_delta=access_expires,
            extra_claims={"email": user.email},
        )

        raw_refresh_token = create_token(
            subject=user.id,
            expires_delta=refresh_expires,
            extra_claims={"type": "refresh"},
        )

        # Store a hash of the refresh token for revocation/rotation.
        from app.security.password import hash_password as hash_refresh

        token_hash = hash_refresh(raw_refresh_token)
        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now + refresh_expires,
        )
        self.db.add(refresh_record)
        self.db.flush()

        return access_token, raw_refresh_token
