from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator

from app.config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    pass


# Fallback to a local SQLite database when DATABASE_URL is not configured.
_database_url = (
    str(settings.DATABASE_URL)
    if settings.DATABASE_URL is not None
    else "sqlite:///./psxviewai_dev.db"
)

engine = create_engine(
    _database_url,
    future=True,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator:
    from sqlalchemy.orm import Session

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
