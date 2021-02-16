import logging

from datetime import datetime
from typing import List, Union
from pandas import DataFrame
from collections import OrderedDict
from logging import Logger
from market_data import MarketData
from signals import BuySignal, SellSignal
from uuid import UUID
from indicators import SmoothedMovingAverage, Indicator

logger: Logger = logging.getLogger("__main__")


class MovingAverageStrategy:

    def __init__(self):
        self.name: str = "Moving Average Strategy"
        self.profit_target: float = 1.05
        self.indicators: List[Indicator] = list()  # Necessary for backtest plotting
        self.sma_to_price_difference: float = 1.03  # The difference between price and sma -> if met create buy signal

    def check_buy_condition(self, market_data_df: DataFrame) -> Union[BuySignal, bool]:
        """
        Checks if the latest price data meets the conditions of our strategy.

        Parameters:
            market_data_df: Data frame of our market data object containing the current price data

        Returns:
            Either a buy signal if the strategy condition was met, or False if not
        """
        # Get the newest entry
        latest_entry: DataFrame = market_data_df.iloc[-1]
        price: float = latest_entry["price"]
        sma: float = latest_entry["sma"]

        # Check if we meet our strategy condition
        if sma > self.sma_to_price_difference * price:
            return BuySignal(price, latest_entry["time"])
        else:
            return False

    def check_sell_condition(self, market_data: MarketData, not_sold_buys: List[BuySignal]
                             ) -> Union[List[SellSignal], bool]:
        """
        Checks whether the current price meets any target goals of the coins that have not been sold yet.

        Parameters:
            - market_data: The market data on which we will evaluate
            - not_sold_buys: The buy signals that have not had a corresponding sell signal yet

        Returns:
            Either a list of sell signals or False if none got created
        """
        sell_signals: List[SellSignal] = list()
        time, price = market_data.get_latest_entry()
        for buy_signal in not_sold_buys:
            if price >= buy_signal.price * self.profit_target:
                sell_signals.append(SellSignal(buy_signal.signal_id, price, time))
        if sell_signals:
            return sell_signals
        else:
            return False

    def add_indicators(self, price_data: DataFrame, column_name: str) -> DataFrame:
        """
        Adds all indicators that are needed for this strategy to the market data.

        Parameters:
            price_data: The data frame containing the data (e.g. candlestick data)
            column_name: The name of the data frame column on which we will calculate the indicator

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
            price_data: The data frame containing the price data to which we want to add the sma
            indicator_name: The name of the indicator
            column_name: The name of the column on which on which we want to calculate the data on
            period: time period the sma will follow
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

    def calc_sell_signals(self, candlestick_df: DataFrame, buy_signals: OrderedDict) -> OrderedDict:
        """
        Calculates sell signals for a backtest, based on buy signals (profit target) that got calculated before.

        Parameters:
            candlestick_df: The data frame containing the historical price data in form of klines/candles
            buy_signals: The buy signals that we have calculated before

        Returns:
            A ordered dict containing all sell signals ordered buy the time of insert
        """
        logger.info("Calculating sell signals...")

        df: DataFrame = candlestick_df
        sell_signals: OrderedDict[UUID, SellSignal] = OrderedDict()

        for signal_id, signal in buy_signals.items():
            selling_price: float = signal.price * self.profit_target
            time: datetime = signal.time

            # Query all candles that are older than the buying time and also meet our desired selling price
            sell_entries: DataFrame = df.loc[(df["time"] >= time) & (df["high"] >= selling_price)]
            if not sell_entries.empty:
                sell_entry: DataFrame = sell_entries.iloc[0]  # Get the first of those entries
                time = sell_entry["time"]  # Time of sell
                signal: SellSignal = SellSignal(signal_id, selling_price, time)  # Create sell signal
                sell_signals[signal.signal_id] = signal

        return sell_signals
