import logging

from uuid import UUID
from logging import Logger
from datetime import datetime

logger: Logger = logging.getLogger("__main__")


class BuyTransaction:
    def __init__(self, signal_id: UUID, symbol: str, buy_price: float, buy_quantity: float, time: datetime) -> None:
        self.transaction_id: UUID = signal_id  # The transaction id will be the id of the corresponding buy signal
        self.symbol: str = symbol
        self.buy_quantity: float = buy_quantity  # In coins (what we get)
        self.buy_price: float = buy_price  # In euros (what we pay)
        self.time: datetime = time


class SellTransaction:
    def __init__(self, signal_id: UUID, symbol: str, sell_price: float, sell_quantity: float, time: datetime) -> None:
        self.transaction_id: UUID = signal_id  # The transaction id will be the id of the corresponding sell signal
        self.symbol: str = symbol
        self.sell_quantity: float = sell_price  # In coins (what we pay)
        self.sell_price: float = sell_quantity  # In euros (what we get)
        self.time: datetime = time
