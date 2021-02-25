import logging

from datetime import datetime
from typing import List, Union
from pandas import DataFrame, Series
from collections import OrderedDict
from logging import Logger
from buy_signal import BuySignal
from uuid import UUID
from indicators import SmoothedMovingAverage, Indicator
from strategies.strategy import Strategy

logger: Logger = logging.getLogger("__main__")


class MovingAverageStrategy(Strategy):

    INDICATOR_NAME_SLOW_SMA = "slow_sma"

    def __init__(self):
        self.name: str = "Moving Average Strategy"
        self.profit_target: float = 1.05
        self.stop_loss_target: float = 0.85
        self.sma_to_price_difference: float = 1.03  # The difference between price and sma -> if met create buy signal
        self.indicators: List[Indicator] = list()  # Necessary for backtest plotting

    def check_buy_condition(self, price: float, time: datetime, row: Series = None) -> Union[BuySignal, bool]:
        """
        Checks whether the latest price data meets the conditions of our strategy.

        Parameters:
            - price: (Decimal) Price for which we want to check the buy condition
            - time: (datetime) Time of the given price
            - row: Data frame row holding all the additional values like indicators
        Returns:
            Either a buy signal if the strategy condition was met, or False if not
        """
        sma: float = getattr(row, self.INDICATOR_NAME_SLOW_SMA)

        # Check if we meet our strategy condition
        if sma > self.sma_to_price_difference * price:
            return BuySignal(price, time)
        else:
            return False

    def add_indicators(self, price_data: DataFrame, column_name: str) -> DataFrame:
        """
        Adds all indicators that are needed for this strategy to the market data.

        Parameters:
            - price_data: The data frame containing the data (e.g. candlestick data)
            - column_name: The name of the data frame column on which we will calculate the indicator

        Return:
            A data frame containing the price data and all indicators added by this strategy
        """
        self.indicators = list()  # Reset list of added indicators
        price_data: DataFrame = self.add_sma(price_data, "slow_sma", column_name, 50)
        return price_data

    def add_sma(self, price_data: DataFrame, indicator_name: str, column_name: str, period: int) -> DataFrame:
        """
        Adds the indicator SmoothedMovingAverage to the price data df.

        Parameters:
            - price_data: The data frame containing the price data to which we want to add the sma
            - indicator_name: The name of the indicator
            - column_name: The name of the column on which on which we want to calculate the data on
            - period: time period the sma will follow
        """
        sma: SmoothedMovingAverage = SmoothedMovingAverage(indicator_name, period)  # Create new indicator
        df: DataFrame = sma.add_data(price_data, column_name)  # Add indicator data to the candlestick data
        self.indicators.append(sma)
        return df

    def calc_buy_signals(self, candlestick_df: DataFrame) -> OrderedDict:
        """
        Calculates buy signals for a backtest.

        Parameters:
            candlestick_df: The data frame containing the historical price data in form of klines/candlesticks

        Returns:
            A ordered dict containing all buy signals ordered by the time of insert
        """
        logger.info("Calculating buy signals...")

        df: DataFrame = candlestick_df
        buy_signals: OrderedDict[UUID, BuySignal] = OrderedDict()

        for i in range(1, len(df["close"])):
            if df["slow_sma"][i] > (self.sma_to_price_difference * df["low"][i]):
                time: datetime = df["time"][i]  # time of buy
                price: float = df["low"][i]
                signal: BuySignal = BuySignal(price, time)  # Append buy signal to list of buy signals
                buy_signals[signal.signal_id] = signal

        return buy_signals
