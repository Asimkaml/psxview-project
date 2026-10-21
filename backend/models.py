"""Core SQLAlchemy models for authentication and saved valuations."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)

    otps = relationship("OtpCode", back_populates="user", cascade="all, delete-orphan")
    valuations = relationship("SavedValuation", back_populates="user", cascade="all, delete-orphan")


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    code = Column(String(6), nullable=False, index=True)
    purpose = Column(String(20), nullable=False)  # e.g. "login", "register"
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    consumed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="otps")


class SavedValuation(Base):
    __tablename__ = "saved_valuations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    symbol = Column(String(20), nullable=False, index=True)
    eps = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    inputs_json = Column(Text, nullable=False)
    result_json = Column(Text, nullable=False)

    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="valuations")
