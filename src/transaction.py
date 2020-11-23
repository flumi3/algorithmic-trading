import logging

from datetime import datetime
from logging import Logger

logger: Logger = logging.getLogger(__name__)


class Transaction:

    def __init__(self, t_type: str, trading_fee: float, price: float, time: datetime, backtest: bool = True) -> None:
        logger.info(f"Creating new {t_type} transaction...")

        self.type: str = t_type
        self.trading_fee: float = trading_fee
        self.price: float = price
        self.net_price: float = price - price * trading_fee  # subtract trading fee from price
        self.time: datetime = time
