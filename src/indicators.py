import logging

from pandas import DataFrame
from logging import Logger
from pyti.smoothed_moving_average import smoothed_moving_average as sma
from abc import ABC, abstractmethod

logger: Logger = logging.getLogger("__main__")


# Parent class 
class Indicator(ABC):
    def __init__(self, name: str) -> None:
        self.name: str = name

    @abstractmethod
    def add_data(self, data: DataFrame, column_name: str):
        # Needs to be overridden in every subclass
        raise NotImplementedError("Missing implementation: Please override this method in the subclass")


# Subclass
class SmoothedMovingAverage(Indicator):

    def __init__(self, name: str, period: int) -> None:
        logger.info(f"Creating new indicator {name}...")
        super().__init__(name)  # Init parent class
        self.period: int = period

    def add_data(self, data: DataFrame, column_name: str) -> DataFrame:
        """
        Adds smoothed moving average to the data.

        Parameters:
            - data: (DataFrame) The data frame to which we will add the sma
            - column_name: (str) The name of the column containing the data on which we calculate the sma

        Return:
            data: (DataFrame) The frame that now contains the indicator
        """
        logger.info(f"Adding indicator '{self.name}' to market data...")
        data[self.name] = sma(data[column_name].tolist(), self.period)
        return data
