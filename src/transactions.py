import logging

from uuid import UUID
from logging import Logger
from datetime import datetime

logger: Logger = logging.getLogger(__name__)


class BuyTransaction:
    def __init__(self, signal_id: UUID, symbol: str, price: float, quantity: float, time: datetime, test: bool) -> None:
        self.transaction_id: UUID = signal_id  # The transaction id will be the id of the corresponding buy signal
        self.symbol: str = symbol
        self.price: float = price  # In euros (what we pay)
        self.quantity: float = quantity  # In coins (what we get)
        self.time: datetime = time
        self.test: bool = test


class SellTransaction:
    def __init__(self, signal_id: UUID, symbol: str, price: float, quantity: float, time: datetime, test: bool) -> None:
        self.transaction_id: UUID = signal_id  # The transaction id will be the id of the corresponding sell signal
        self.symbol: str = symbol
        self.price: float = price  # In coins (what we pay)
        self.quantity: float = quantity  # In euros (what we get)
        self.time: datetime = time
        self.test: bool = test
