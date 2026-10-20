from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MarketPriceSnapshot:
    instrument_symbol: str
    price: float
    currency: str
    source: str
    as_of: datetime  # market timestamp
    retrieved_at: datetime
    is_delayed: bool


class MarketDataProvider(ABC):
    """Abstraction over external PSX market-data sources.

    Concrete adapters (e.g. using `psxdata`) will implement this later.
    """

    @abstractmethod
    def get_latest_price(self, instrument_symbol: str) -> Optional[MarketPriceSnapshot]:
        raise NotImplementedError


class InMemoryMarketDataProvider(MarketDataProvider):
    """Simple in-memory provider for tests and local development."""

    def __init__(self) -> None:
        self._data: dict[str, MarketPriceSnapshot] = {}

    def set_price(self, snapshot: MarketPriceSnapshot) -> None:
        self._data[snapshot.instrument_symbol] = snapshot

    def get_latest_price(self, instrument_symbol: str) -> Optional[MarketPriceSnapshot]:
        return self._data.get(instrument_symbol)
