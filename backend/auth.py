"""Authentication router: register/login with password + OTP 2FA and sessions."""
from __future__ import annotations

import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from config import config
from db import get_db
from emailer import send_otp_email
from models import OtpCode, User
from security import (
    create_challenge_token,
    create_session_token,
    decode_token,
    generate_otp_code,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class OtpIn(BaseModel):
    token: str
    code: str


class UserOut(BaseModel):
    id: int
    email: EmailStr


def _issue_session(response: Response, user: User) -> dict:
    token = create_session_token(str(user.id))
    response.set_cookie(
        key=config.cookie_name,
        value=token,
        httponly=True,
        secure=config.cookie_secure,
        samesite="lax",
    )
    return {"id": user.id, "email": user.email}


@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise HTTPException(400, "Email already registered")

    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    code = generate_otp_code()
    now = dt.datetime.utcnow()
    otp = OtpCode(
        user_id=user.id,
        code=code,
        purpose="register",
        created_at=now,
        expires_at=now + dt.timedelta(minutes=10),
    )
    db.add(otp)
    db.commit()

    send_otp_email(user.email, code)

    token = create_challenge_token(str(user.id))
    return {"challenge_token": token}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form.username))
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(400, "Invalid email or password")

    code = generate_otp_code()
    now = dt.datetime.utcnow()
    otp = OtpCode(
        user_id=user.id,
        code=code,
        purpose="login",
        created_at=now,
        expires_at=now + dt.timedelta(minutes=10),
    )
    db.add(otp)
    db.commit()

    send_otp_email(user.email, code)

    token = create_challenge_token(str(user.id))
    return {"challenge_token": token}


def _consume_otp(db: Session, user: User, code: str, purpose: str) -> None:
    now = dt.datetime.utcnow()
    stmt = select(OtpCode).where(
        and_(
            OtpCode.user_id == user.id,
            OtpCode.purpose == purpose,
            OtpCode.code == code,
            OtpCode.expires_at >= now,
            OtpCode.consumed_at.is_(None),
        )
    ).order_by(OtpCode.id.desc())
    otp = db.scalars(stmt).first()
    if not otp:
        raise HTTPException(400, "Invalid or expired code")
    otp.consumed_at = now
    db.add(otp)
    db.commit()


@router.post("/verify-otp")
def verify_otp(data: OtpIn, response: Response, db: Session = Depends(get_db)):
    try:
        payload = decode_token(data.token, expected_kind="challenge")
    except Exception:
        raise HTTPException(400, "Invalid challenge token")

    user_id = int(payload.get("sub"))
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(400, "User not found")

    _consume_otp(db, user, data.code, purpose="login")

    return _issue_session(response, user)


def _get_session_user(db: Session, token: str) -> Optional[User]:
    from jwt import InvalidTokenError, ExpiredSignatureError

    try:
        payload = decode_token(token, expected_kind="session")
    except (InvalidTokenError, ExpiredSignatureError):
        return None
    user_id = int(payload.get("sub"))
    user = db.get(User, user_id)
    if not user or not user.is_active:
        return None
    return user


def get_current_user(response: Response, db: Session = Depends(get_db)) -> User:
    from fastapi import Cookie

    token: Optional[str] = Cookie(default=None, alias=config.cookie_name)
    if not token:
        raise HTTPException(401, "Not authenticated")
    user = _get_session_user(db, token)
    if not user:
        # Clear cookie on invalid session
        response.delete_cookie(config.cookie_name)
        raise HTTPException(401, "Not authenticated")
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(config.cookie_name)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(id=user.id, email=user.email)
