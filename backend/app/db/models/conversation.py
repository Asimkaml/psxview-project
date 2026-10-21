from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user = relationship("User")
    answers: Mapped[list["Answer"]] = relationship(
        "Answer", back_populates="conversation", cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_as_of: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    conversation = relationship("Conversation", back_populates="answers")
    user = relationship("User")
    claims: Mapped[list["AnswerClaim"]] = relationship(
        "AnswerClaim", back_populates="answer", cascade="all, delete-orphan"
    )


class AnswerClaim(Base):
    __tablename__ = "answer_claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    answer_id: Mapped[int] = mapped_column(
        ForeignKey("answers.id"), index=True, nullable=False
    )
    claim_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    evidence_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("evidence_items.id"), index=True, nullable=True
    )
    valuation_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("valuation_runs.id"), index=True, nullable=True
    )

    answer = relationship("Answer", back_populates="claims")
    evidence_item = relationship("EvidenceItem")
    valuation_run = relationship("ValuationRun")
