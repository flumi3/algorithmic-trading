from abc import ABC, abstractmethod
from datetime import datetime
from pandas import DataFrame

EXCEPTION_MESSAGE: str = "Missing implementation: Please override this method in the subclass"


class Strategy(ABC):

    @abstractmethod
    def check_buy_condition(self, price: float, time: datetime, row=None):
        raise NotImplementedError(EXCEPTION_MESSAGE)

    @abstractmethod
    def add_indicators(self, price_data: DataFrame, column_name: str):
        raise NotImplementedError(EXCEPTION_MESSAGE)
