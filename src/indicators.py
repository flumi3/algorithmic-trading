import logging

from pandas import DataFrame
from logging import Logger
from pyti.smoothed_moving_average import smoothed_moving_average as sma

logger: Logger = logging.getLogger("__main__")


# Parent class 
class Indicator:
    def __init__(self, name: str) -> None:
        self.name: str = name
    

# Subclass
class SmoothedMovingAverage(Indicator):

    def __init__(self, name: str, period: int) -> None:
        logger.info(f"Creating new indicator {name}...")
        Indicator.__init__(self, name)  # Init parent class
        self.period: int = period

    def add_data(self, data: DataFrame, column_name: str) -> DataFrame:
        """
        Adds smoothed moving average to the data.

        Parameters:
            data: The data frame to which we will add the sma
            column_name: The name of the column containing the data on which we calculate the sma

        Return:
            The data frame that now contains the indicator
        """
        logger.info(f"Adding indicator '{self.name}' to market data...")
        data[self.name] = sma(data[column_name].tolist(), self.period)
        return data
