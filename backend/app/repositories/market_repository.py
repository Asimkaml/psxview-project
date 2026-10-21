from collections.abc import Iterable

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import MarketPrice


class MarketPriceRepository:
    """Read/write helpers for `MarketPrice` snapshots."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, snapshot: MarketPrice) -> MarketPrice:
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def get_latest_for_instrument_ids(
        self, instrument_ids: Iterable[int]
    ) -> dict[int, MarketPrice]:
        ids = list({int(i) for i in instrument_ids})
        if not ids:
            return {}

        # Fetch all rows ordered so that the first per instrument is the latest.
        rows = (
            self.db.query(MarketPrice)
            .filter(MarketPrice.instrument_id.in_(ids))
            .order_by(MarketPrice.instrument_id, desc(MarketPrice.as_of))
            .all()
        )

        latest: dict[int, MarketPrice] = {}
        for row in rows:
            if row.instrument_id not in latest:
                latest[row.instrument_id] = row
        return latest
