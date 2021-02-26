import logging

from datetime import datetime
from logging import Logger
from typing import Union, List, Dict
from uuid import UUID
from pandas import DataFrame
from prompt_toolkit import prompt
from api.binance import Binance
from cli.validators import YesNoValidator
from buy_signal import BuySignal
from market_data import MarketData
from strategies.moving_average_strategy import MovingAverageStrategy
from transactions import BuyTransaction, SellTransaction

logger: Logger = logging.getLogger("__main__")


class Bot:
    STATUS_RUNNING: str = "running"  # Bot is actively running
    STATUS_INIT: str = "init"  # Bot got created but did not start to trade yet and has not traded before
    STATUS_ABORTED: str = "aborted"  # Bot encountered an exception which interrupted the bot
    STATUS_PAUSED: str = "paused"  # The bot got paused by the user

    def __init__(self, name: str, symbol: str, api: Union[Binance], strategy: Union[MovingAverageStrategy],
                 starting_capital: float, buy_quantity: float, description: str = "") -> None:
        self.id: int = -1  # Until the bot is not managed by the bot runner, its id will be -1
        self.name = name
        self.symbol = symbol
        self.api: Union[Binance] = api
        self.strategy: Union[MovingAverageStrategy] = strategy
        self.starting_capital: float = starting_capital  # Decides how much capital the bot is allowed to use
        self.capital: float = starting_capital
        self.buy_quantity: float = buy_quantity
        self.description: str = description
        self.market_data: MarketData = self.__get_init_data()  # Create market data with historical price data
        self.buy_signals: List[BuySignal] = list()
        self.buy_transactions: List[BuyTransaction] = list()
        self.sell_transactions: List[SellTransaction] = list()
        self.not_sold_yet: Dict[UUID, BuySignal] = dict()
        self.status = self.STATUS_INIT

    def __get_init_data(self) -> MarketData:
        logger.info(f"Collecting initial market data for bot '{self.name}'...")

        # Calculate limit: 2 months * 30 days * 24 hours * 60 minutes = 86.400 candles
        #   -> Two months of price data for every minute
        limit: int = 2 * 30 * 24 * 60
        candlestick_df: DataFrame = self.api.get_candlestick_data(symbol=self.symbol, interval="1M", limit=limit)

        # Extract only the time and price columns
        times: List[datetime] = candlestick_df["time"].tolist()
        prices: List[float] = candlestick_df["close"].tolist()

        # Create market data object
        market_data: MarketData = MarketData(self.symbol, times, prices)
        return market_data

    def __update_price_data(self) -> None:
        """Adds the current price information to the market data and removes the oldest price information"""
        logger.info(f"Updating price data of bot '{self.name}'...")
        current_time: datetime = self.api.get_server_time()
        current_price: float = self.api.get_current_price(self.symbol)  # Get current price
        self.market_data.add_entry(current_time, current_price)

    def __evaluate_buy(self) -> None:
        # Create data frame from market data
        market_data_df: DataFrame = self.market_data.create_dataframe()

        # Add indicators of the strategy
        market_data_df = self.strategy.add_indicators(market_data_df, "price")

        # Check if we meet the buy conditions of the strategy
        buy_signal: Union[BuySignal, bool] = self.strategy.check_buy_condition(market_data_df)
        if buy_signal:
            if self.capital >= buy_signal.price:
                print("Buy Signal!")
                print(f"Quantity: {self.buy_quantity}")
                print(f"Price: {self.buy_quantity * buy_signal.price}\n")
                user_input: str = prompt("Accept buy signal? [y/n] ", validator=YesNoValidator())
                if user_input == "y":
                    self.__buy(buy_signal)

    def __buy(self, buy_signal: BuySignal):
        logger.info(f"Buying coin for {buy_signal.price}€...")

    def __sell(self):
        logger.info("Selling coin...")

    def run(self):
        pass
