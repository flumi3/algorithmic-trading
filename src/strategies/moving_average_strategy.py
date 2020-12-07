import logging

from datetime import datetime
from pandas import DataFrame
from collections import OrderedDict
from typing import Dict
from logging import Logger
from backtest.signals import BuySignal, SellSignal
from uuid import UUID

logger: Logger = logging.getLogger(__name__)


class MovingAverageStrategy:

    def __init__(self):
        self.name: str = "Moving Average Strategy"
        self.desired_sell_percentage: float = 1.05

    # TODO: maybe assert the candlestick data for sma indicator because it is necessary for this strategy
    #  (maybe validate function)

    @staticmethod
    def calc_buy_signals(candlestick_df: DataFrame) -> OrderedDict:
        logger.info("Calculating buy signals...")

        df: DataFrame = candlestick_df
        buy_signals: OrderedDict[UUID, BuySignal] = OrderedDict()

        for i in range(1, len(df["close"])):
            if df["slow_sma"][i] > (1.03 * df["low"][i]):
                time: datetime = df["time"][i]  # time of buy
                price: float = df["low"][i]
                signal: BuySignal = BuySignal(price, time)  # Append buy signal to list of buy signals
                buy_signals[signal.signal_id] = signal

        return buy_signals

    def calc_sell_signals(self, candlestick_df: DataFrame, buy_signals: OrderedDict) -> OrderedDict:
        logger.info("Calculating sell signals...")

        df: DataFrame = candlestick_df
        sell_signals: OrderedDict[UUID, SellSignal] = OrderedDict()

        for signal_id, signal in buy_signals.items():
            selling_price: float = signal.price * self.desired_sell_percentage
            time: datetime = signal.time

            # Query all candles that are older than the buying time and also meet our desired selling price
            sell_entries: DataFrame = df.loc[(df["time"] >= time) & (df["high"] >= selling_price)]
            if not sell_entries.empty:
                sell_entry: DataFrame = sell_entries.iloc[0]  # Get the first of those entries
                time = sell_entry["time"]  # Time of sell
                signal: SellSignal = SellSignal(signal_id, selling_price, time)  # Create sell signal
                sell_signals[signal.signal_id] = signal

        return sell_signals
