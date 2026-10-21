from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class EvidenceItem(Base):
    """Normalized evidence used to back research claims.

    Links out to source documents or news items and captures a stable excerpt
    with provenance. Numerical metrics will reference evidence IDs separately.
    """

    __tablename__ = "evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id"), index=True, nullable=True
    )
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id"), index=True, nullable=True
    )
    news_article_id: Mapped[int | None] = mapped_column(
        ForeignKey("news_articles.id"), index=True, nullable=True
    )

    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)

    company = relationship("Company")
    document = relationship("Document")
    news_article = relationship("NewsArticle")
