"""Shared FastAPI test fixtures for the PSXviewAI backend."""
from __future__ import annotations

import os
import tempfile
from typing import Callable, Tuple

import pytest
from fastapi.testclient import TestClient

import auth
import emailer
import valuation
from config import Settings, get_settings
from db import Base, get_db
from main import app as real_app
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="session")
def engine():
    # Use a temporary SQLite database file for tests so that multiple
    # connections can share state.
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.db")
        engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        yield engine
        engine.dispose()


@pytest.fixture
def db_session(engine) -> Session:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def app(db_session: Session):
    # Override settings to use a predictable JWT secret and disable secure cookies.
    def override_settings() -> Settings:
        s = Settings()
        s.jwt_secret = "test-secret"
        s.cookie_secure = False
        s.database_url = "sqlite:///:memory:"
        return s

    real_app.dependency_overrides[get_settings] = override_settings

    # Override DB dependency to use the test session.
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    real_app.dependency_overrides[get_db] = override_get_db

    # Ensure routers are included for tests (auth already added in main).
    a = real_app
    a.include_router(auth.router)
    a.include_router(valuation.router)

    yield a

    real_app.dependency_overrides.clear()


@pytest.fixture
def make_user(app) -> Callable[[], Tuple[TestClient, str]]:
    """Create a user and return (client, email)."""

    sent = {}

    def fake_send(email: str, code: str) -> None:
        sent.setdefault(email, []).append(code)

    # Patch the email sender used by auth.
    app.dependency_overrides[emailer.send_otp_email] = fake_send  # type: ignore[assignment]

    client = TestClient(app)

    def _make() -> Tuple[TestClient, str]:
        email = "user@example.com"
        r = client.post("/api/auth/register", json={"email": email, "password": "secret"})
        assert r.status_code == 200
        challenge = r.json()["challenge_token"]
        code = sent[email][0]
        r = client.post("/api/auth/verify-otp", json={"token": challenge, "code": code})
        assert r.status_code == 200
        assert r.json()["email"] == email
        return client, email

    return _make
