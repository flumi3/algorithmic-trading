import logger

from datetime import datetime
from logging import Logger

logger: Logger = logger.get_main_logger()


class Transaction:

    def __init__(self, type: str, trading_fee: float, price: float, time: datetime, backtest: bool = True) -> None:
        logger.info(f"Creating new {type} transaction...")

        self.type: str = type
        self.trading_fee: float = trading_fee
        self.price: float = price
        self.net_price: float = price - price * trading_fee  # subtract trading fee from price
        self.time: datetime = time
        
