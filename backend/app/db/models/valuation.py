from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ValuationRun(Base):
    """A set of valuation scenarios for a company at a point in time."""

    __tablename__ = "valuation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=True
    )
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    inputs_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    company = relationship("Company")
    user = relationship("User")
    scenarios: Mapped[list["ValuationScenario"]] = relationship(
        "ValuationScenario", back_populates="run", cascade="all, delete-orphan"
    )


class ValuationScenario(Base):
    __tablename__ = "valuation_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("valuation_runs.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(20), nullable=False)  # bear/base/bull
    fair_value_per_share: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    upside_downside_pct: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)

    run = relationship("ValuationRun", back_populates="scenarios")
