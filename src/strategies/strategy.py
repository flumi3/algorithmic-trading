from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, OrderedDict
from pandas import DataFrame
from market_data import MarketData
from buy_signal import BuySignal

EXCEPTION_MESSAGE: str = "Missing implementation: Please override this method in the subclass"


class Strategy(ABC):

    @abstractmethod
    def check_buy_condition(self, price: float, time: datetime, row=None):
        raise NotImplementedError

    @abstractmethod
    def add_indicators(self, price_data: DataFrame, column_name: str):
        raise NotImplementedError

    @abstractmethod
    def calc_buy_signals(self, candlestick_df: DataFrame):
        raise NotImplementedError
