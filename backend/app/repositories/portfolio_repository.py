from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models import Holding, WatchlistEntry


class WatchlistRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_user(self, user_id: int) -> list[WatchlistEntry]:
        return (
            self.db.query(WatchlistEntry)
            .filter(WatchlistEntry.user_id == user_id)
            .order_by(WatchlistEntry.created_at)
            .all()
        )

    def get_for_user(self, user_id: int, entry_id: int) -> WatchlistEntry | None:
        return (
            self.db.query(WatchlistEntry)
            .filter(
                WatchlistEntry.user_id == user_id,
                WatchlistEntry.id == entry_id,
            )
            .one_or_none()
        )

    def get_by_instrument(self, user_id: int, instrument_id: int) -> WatchlistEntry | None:
        return (
            self.db.query(WatchlistEntry)
            .filter(
                WatchlistEntry.user_id == user_id,
                WatchlistEntry.instrument_id == instrument_id,
            )
            .one_or_none()
        )

    def add(self, user_id: int, instrument_id: int) -> WatchlistEntry:
        entry = WatchlistEntry(user_id=user_id, instrument_id=instrument_id)
        self.db.add(entry)
        self.db.flush()
        self.db.refresh(entry)
        return entry

    def delete(self, entry: WatchlistEntry) -> None:
        self.db.delete(entry)


class HoldingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_user(self, user_id: int) -> list[Holding]:
        return (
            self.db.query(Holding)
            .filter(Holding.user_id == user_id)
            .order_by(Holding.created_at)
            .all()
        )

    def get_for_user(self, user_id: int, holding_id: int) -> Holding | None:
        return (
            self.db.query(Holding)
            .filter(Holding.user_id == user_id, Holding.id == holding_id)
            .one_or_none()
        )

    def get_by_instrument(self, user_id: int, instrument_id: int) -> Holding | None:
        return (
            self.db.query(Holding)
            .filter(
                Holding.user_id == user_id,
                Holding.instrument_id == instrument_id,
            )
            .one_or_none()
        )

    def upsert(
        self,
        *,
        user_id: int,
        instrument_id: int,
        quantity: Decimal,
        average_cost: Decimal,
        currency: str = "PKR",
    ) -> Holding:
        holding = self.get_by_instrument(user_id, instrument_id)
        if holding is None:
            holding = Holding(
                user_id=user_id,
                instrument_id=instrument_id,
                quantity=quantity,
                average_cost=average_cost,
                currency=currency,
            )
            self.db.add(holding)
        else:
            holding.quantity = quantity
            holding.average_cost = average_cost
            holding.currency = currency or holding.currency

        self.db.flush()
        self.db.refresh(holding)
        return holding

    def delete(self, holding: Holding) -> None:
        self.db.delete(holding)
