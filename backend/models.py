"""Database tables."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


def utcnow() -> datetime:
    """Return the current UTC datetime (used for default timestamps)."""
    return datetime.now(timezone.utc)


class User(Base):
    """Registered application users."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class OtpCode(Base):
    """
    One row per emailed 2FA code.

    We store a HASH of the code, never the plain code itself.
    The hash is compared at verification time and the row is marked used.
    """
    __tablename__ = "otp_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class SavedValuation(Base):
    """
    A valuation a user has saved to revisit later.

    Inputs and results are stored as JSON strings so the schema does not need
    to change if the valuation shape evolves.
    """
    __tablename__ = "saved_valuations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(20))
    eps: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    inputs_json: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)