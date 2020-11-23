import logging

from datetime import datetime
from pandas import DataFrame
from typing import List
from api.binance import Binance
from transaction import Transaction
from logging import Logger

logger: Logger = logging.getLogger(__name__)


class MovingAverageStrategy:

    # TODO: maybe assert the candlestick data for sma indicator because it is necessary for this strategy (maybe validate function)

    @staticmethod
    def calc_buy_signals(candlestick_df: DataFrame) -> List[Transaction]:
        logger.info("Calculating buy signals...")

        df: DataFrame = candlestick_df
        buy_signals: List[Transaction] = list()

        for i in range(1, len(df["close"])):
            if df["slow_sma"][i] > (1.03 * df["low"][i]):
                time: datetime = df["time"][i]  # time of buy
                buying_price: float = df["low"][i]

                # Append buy signal to list of buy signals
                buy: Transaction = Transaction("buy", Binance.TRADING_FEE, buying_price, time, True)
                buy_signals.append(buy)

        return buy_signals

    @staticmethod
    def calc_sell_signals(candlestick_df: DataFrame, desired_sell: float, buy_signals: List[Transaction]) -> List[Transaction]:
        logger.info("Calculating sell signals...")

        df: DataFrame = candlestick_df
        sell_signals: List[Transaction] = list()

        for signal in buy_signals:
            buying_price: float = signal.price
            selling_price: float = buying_price * desired_sell
            time: datetime = signal.time

            # Query all candles that are older than the buying time and also meet our desired selling price
            sell_entries: DataFrame = df.loc[(df["time"] >= time) & (df["high"] >= selling_price)]
            if not sell_entries.empty:
                sell_entry: DataFrame = sell_entries.iloc[0]  # Get the first of those entries
                time = sell_entry["time"]  # Time of sell
                sell: Transaction = Transaction("sell", Binance.TRADING_FEE, selling_price, time, True)
                sell_signals.append(sell)
        
        return sell_signals






