from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    primary_company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id"), index=True, nullable=True
    )

    text_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)

    primary_company = relationship("Company")
    company_links: Mapped[list["NewsCompanyLink"]] = relationship(
        "NewsCompanyLink", back_populates="news_article", cascade="all, delete-orphan"
    )


class NewsCompanyLink(Base):
    """Many-to-many mapping between news and affected companies."""

    __tablename__ = "news_company_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    news_article_id: Mapped[int] = mapped_column(
        ForeignKey("news_articles.id"), index=True, nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), index=True, nullable=False
    )

    news_article = relationship("NewsArticle", back_populates="company_links")
    company = relationship("Company")
