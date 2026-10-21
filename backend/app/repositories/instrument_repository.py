from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.db.models import Instrument


class InstrumentRepository:
    """Data access helpers for instruments.

    Instruments are referenced by their `symbol` in external APIs and the
    frontend. This repository resolves symbols to internal IDs.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_symbol(self, symbol: str) -> Instrument | None:
        normalized = symbol.strip().upper()
        return (
            self.db.query(Instrument)
            .filter(Instrument.symbol == normalized)
            .one_or_none()
        )

    def get_by_symbols(self, symbols: Iterable[str]) -> list[Instrument]:
        normalized = {s.strip().upper() for s in symbols}
        if not normalized:
            return []
        return (
            self.db.query(Instrument)
            .filter(Instrument.symbol.in_(normalized))
            .all()
        )
