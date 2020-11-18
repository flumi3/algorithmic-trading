from typing import List
from pandas import DataFrame
from indicators import Indicator, SmoothedMovingAverage


class MarketData:

    def __init__(self, data: DataFrame, ) -> None:
        self.candlestick_data: DataFrame = data
        self.indicators: List[Indicator] = list()  # List of indicators to keep track of the indicators contained by this data

    def add_SMA(self, name: str, period: int) -> None:
        sma = SmoothedMovingAverage(name, period)  # Create new indicator
        sma.add_data(self.candlestick_data)  # Add indicator data to the candlestick data
        self.indicators.append(sma)
