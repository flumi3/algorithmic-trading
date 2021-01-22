import logging
from datetime import datetime

from logging import Logger
from typing import List

from pandas import DataFrame

logger: Logger = logging.getLogger("__main__")


class MarketData:

    def __init__(self, symbol: str, init_times: List[datetime], init_prices: List[float]) -> None:
        logger.info("Creating new market data...")
        self.symbol: str = symbol
        self.times: List[datetime] = init_times
        self.prices: List[float] = init_prices

    def add_entry(self, time: datetime, price: float):
        # Append entry to the end
        self.times.append(time)
        self.prices.append(price)
        # Remove oldest entry to keep the same amount of entries
        self.times.pop(0)
        self.prices.pop(0)

    def create_dataframe(self) -> DataFrame:
        return DataFrame(list(zip(self.times, self.prices)), columns=["time", "price"])


# market data mit einem data property das einen dataframe hält. dataframe enthält bestimmte feste anzahl an entries,
# welche man vorher angeben muss. entries bestehen nur aus zeit und preis. es gibt dann eine add entry methode die
# einen neuen entry hinten anhängt und den ältesten entry aus dem df löscht, um das limit einzuhalten. dann kann man
# immer das gleiche market data object verwalten und auf kopien dessen die indicator anwenden und check ob der neueste
# entry die strat conditions matched