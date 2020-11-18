import logger

from datetime import datetime
from pandas import DataFrame
from typing import List
from api.binance import Binance
from transaction import Transaction
from logging import Logger

logger: Logger = logger.get_main_logger()


class MovingAvergageStrategy:

    # TODO: maybe assert the candlestick data for sma indicator because it is necessary for this strategy (maybe validate function)

    def calc_buy_signals(self, candlestick_df: DataFrame) -> List[Transaction]:
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

    def calc_sell_signals(self, candlestick_df: DataFrame, desired_sell: float, buy_signals: List[Transaction]) -> List[Transaction]:
        logger.info("Calculating sell signals...")

        df: DataFrame = candlestick_df
        sell_signals: List[Transaction] = list()

        for signal in buy_signals:
            buying_price: float = signal.price
            selling_price: float = buying_price * desired_sell
            time: datetime = signal.time

            # Query the entry (candle) of which the point in time is the same as the buy signal in order to only loop
            # from this point in time through the dataframe
            index: int = df.index[df["time"] == time].tolist()[0]
            for i in range(index, len(df["close"])):
                if df["high"][i] >= selling_price:
                    time: datetime = df["time"][i]  # Time of sell
                    sell: Transaction = Transaction("sell", Binance.TRADING_FEE, selling_price, time, True)
                    sell_signals.append(sell)
                    break
        
        return sell_signals






