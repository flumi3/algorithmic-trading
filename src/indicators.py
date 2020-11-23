import logging

from pandas import DataFrame
from logging import Logger
from pyti.smoothed_moving_average import smoothed_moving_average as sma

logger: Logger = logging.getLogger(__name__)


# Parent class 
class Indicator:
    def __init__(self, name: str) -> None:
        self.__name: str = name

    def get_name(self) -> str:
        return self.__name
    

# Subclass
class SmoothedMovingAverage(Indicator):
    def __init__(self, name: str, period: int) -> None:
        logger.info(f"Creating new indicator {name}...")
        Indicator.__init__(self, name)  # Init parent class
        self.__period: int = period

    def add_data(self, candlestick_data: DataFrame):
        logger.info(f"Adding indicator {self.get_name()} to market data...")
        df: DataFrame = candlestick_data
        df[self.get_name()] = sma(df["close"].tolist(), self.__period)

