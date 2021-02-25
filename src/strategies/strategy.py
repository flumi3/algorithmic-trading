from abc import ABC, abstractmethod
from typing import List, OrderedDict
from pandas import DataFrame
from market_data import MarketData
from signals import BuySignal

EXCEPTION_MESSAGE: str = "Missing implementation: Please override this method in the subclass"


class Strategy(ABC):

    @abstractmethod
    def check_buy_condition(self, market_data_df: DataFrame):
        raise NotImplementedError

    @abstractmethod
    def check_sell_condition(self, market_data: MarketData, not_sold_buys: List[BuySignal]):
        raise NotImplementedError

    @abstractmethod
    def add_indicators(self, price_data: DataFrame, column_name: str):
        raise NotImplementedError

    @abstractmethod
    def calc_buy_signals(self, candlestick_df: DataFrame):
        raise NotImplementedError

    @abstractmethod
    def calc_sell_signals(self, candlestick_df: DataFrame, buy_signals: OrderedDict):
        raise NotImplementedError
