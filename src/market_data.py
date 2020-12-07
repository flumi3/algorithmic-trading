import logging

from typing import List
from pandas import DataFrame
from indicators import Indicator, SmoothedMovingAverage
from logging import Logger

logger: Logger = logging.getLogger(__name__)


class MarketData:

    def __init__(self, data: DataFrame) -> None:
        logger.info("Creating new market data...")
        self.candlestick_data: DataFrame = data
        self.indicators: List[Indicator] = list()  # List of indicators to keep track of the contained indicators

    def add_sma(self, name: str, period: int) -> None:
        sma = SmoothedMovingAverage(name, period)  # Create new indicator
        sma.add_data(self.candlestick_data)  # Add indicator data to the candlestick data
        self.indicators.append(sma)
