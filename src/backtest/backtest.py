import logging

from datetime import datetime, date
from logging import Logger
from plotly.graph_objs import Candlestick, Layout, Figure, Scatter
from typing import List, Tuple, IO, Union, Dict
from collections import OrderedDict
from market_data import MarketData
from indicators import SmoothedMovingAverage
from backtest.signals import BuySignal, SellSignal
from uuid import UUID
from pandas import DataFrame
from transactions import BuyTransaction, SellTransaction
from util import TerminalColors as Color

logger: Logger = logging.getLogger("__main__")


class Backtest:

    def __init__(self, symbol: str, api_name: str, strategy_name: str, capital: float, buy_quantity: float,
                 trading_fee: float, market_data: MarketData, buy_signals: OrderedDict = None,
                 sell_signals: OrderedDict = None) -> None:
        # Backtest configuration
        self.symbol = symbol
        self.api: str = api_name
        self.strategy: str = strategy_name
        self.starting_capital: float = capital
        self.buy_quantity: float = buy_quantity
        self.trading_fee: float = trading_fee
        # Statistic properties
        self.money_spent: float = 0
        self.money_earned: float = 0
        self.transaction_costs: float = 0  # Sum of the money that got lost in transaction fees
        self.coins_bought: float = 0
        self.coins_sold: float = 0
        # Other
        self.market_data: MarketData = market_data
        self.capital: float = capital
        self.buy_signals: OrderedDict[UUID, BuySignal] = buy_signals
        self.sell_signals: OrderedDict[UUID, SellSignal] = sell_signals
        self.buy_transactions: OrderedDict[UUID, BuyTransaction] = OrderedDict()
        self.sell_transactions: OrderedDict[UUID, SellTransaction] = OrderedDict()
        self.kept_coins: List[UUID] = list()  # List of id's from buy signals that have not been sold yet
        self.capital_over_time: List[Dict[str, float]] = list()  # Represents our capital over the time
        self.capital_over_time.append({"time": self.market_data.candlestick_data["time"][0], "capital": self.capital})

    def create_candlestick_figure(self) -> Figure:
        """Creates a candlestick figure that visualizes the market data of the backtest including the signals"""
        df = self.market_data.candlestick_data  # Access candlestick frame which gets hold by the market data object

        # Plot candlestick chart
        candle: Candlestick = Candlestick(
            x=df["time"],
            open=df["open"],
            close=df["close"],
            high=df["high"],
            low=df["low"],
            name="Candlesticks"
        )
        data: List[object] = [candle]

        # Loop through all indicators of the market data and plot them
        for indicator in self.market_data.indicators:
            # Smoothed moving average
            if type(indicator) == SmoothedMovingAverage:
                sma: Scatter = Scatter(
                    x=df["time"],
                    y=df[indicator.get_name()],
                    name=indicator.get_name(),
                    line=dict(color="rgba(255, 207, 102, 1)")
                )
                data.append(sma)
            # Continue with other indicator types for plotting:
            # if type(indicator) == Indicator...

        # Plot buy signals if we have some
        if self.buy_signals:
            # Lists for values of the accepted buy signals and also the ignored buy signals
            accepted_times, accepted_prices, ignored_times, ignored_prices = self.get_signal_values(self.buy_signals)

            # Create plot for the accepted signals
            accepted_buy_signals: Scatter = Scatter(
                x=accepted_times,
                y=accepted_prices,
                name="Accepted Buy Signals",
                mode="markers",
                line=dict(color="rgba(57, 255, 20, 1)")  # Neon green
            )
            # Create plot for the ignored signals
            ignored_buy_signals: Scatter = Scatter(
                x=ignored_times,
                y=ignored_prices,
                name="Ignored Buy Signals",
                mode="markers",
                line=dict(color="rgba(148, 0, 221, 1)")  # Dark violet
            )
            data.append(accepted_buy_signals)
            data.append(ignored_buy_signals)

        # Plot sell signals if we have some
        if self.sell_signals:
            # Lists for values of the accepted sell signals and also the ignored sell signals
            accepted_times, accepted_prices, ignored_times, ignored_prices = self.get_signal_values(self.sell_signals)

            # Create plot for the accepted sell signals
            accepted_sell_signals: Scatter = Scatter(
                x=accepted_times,
                y=accepted_prices,
                name="Accepted Sell Signals",
                mode="markers",
                line=dict(color="rgba(0, 0, 255, 1)")  # Blue
            )
            # Create plot for the ignored sell signals
            ignored_sell_signals: Scatter = Scatter(
                x=ignored_times,
                y=ignored_prices,
                name="Ignored Sell Signals",
                mode="markers",
                line=dict(color="rgba(139, 69, 19, 1)")  # Brown
            )
            data.append(accepted_sell_signals)
            data.append(ignored_sell_signals)

        # Customize style and display
        layout: Layout = Layout(
            xaxis={
                "title": self.symbol,
                "rangeslider": {"visible": True},
                "type": "date"
            },
            yaxis={
                "fixedrange": False,
                "title": "Price per coin"
            }
        )
        # Create figure and plot it
        figure: Figure = Figure(data=data, layout=layout)
        return figure

    def create_capital_figure(self) -> Figure:
        # Get last entry of our market data and add its time and our current capital to the dict so the chart will not
        # end at the time of the last transaction
        last_time: datetime = self.market_data.candlestick_data["time"].iloc[-1]
        self.capital_over_time.append({"time": last_time, "capital": self.capital})
        capitals_df: DataFrame = DataFrame(self.capital_over_time, columns=["time", "capital"])

        """Creates a plotly figure that represents our capital over the time of the backtest"""
        capital_line: Scatter = Scatter(
            x=capitals_df["time"],
            y=capitals_df["capital"],
            name="Capital [€]",
            line=dict(color="rgba(0, 0, 255, 1)")
        )
        layout: Layout = Layout(
            xaxis={
                "title": "Capital over time",
                "rangeslider": {"visible": False},
                "type": "date"
            },
            yaxis={
                "fixedrange": False,
                "title": "Capital"
            }
        )
        figure: Figure = Figure(capital_line, layout=layout)
        return figure

    def run_backtest(self) -> None:
        logger.info("Running backtest...")

        for buy_signal_id, buy_signal in self.buy_signals.items():
            # Loop through all coins that we have not sold yet and check if we can sell them
            for signal_id in self.kept_coins.copy():  # Copy necessary because we modify the real list whilst iterating
                sell_signal: SellSignal = self.sell_signals.get(signal_id)  # Get corresponding sell signal
                if sell_signal:
                    # Check whether the sell signal occurred before the current buy signal
                    if sell_signal.time <= buy_signal.time:
                        self.sell(signal_id, sell_signal)
                else:
                    logger.debug(f"No existing sell signal for buy signal with ID: {signal_id}")

            # Check whether we have the capital to buy
            buying_price: float = buy_signal.price * self.buy_quantity  # Without transaction fee
            if self.capital >= buying_price:
                self.buy(buy_signal_id, buy_signal)
            else:
                logger.debug("Buy signal ignored! Not enough capital.")

        # Check sell options for all coins we have not sold yet
        for signal_id in self.kept_coins:
            sell_signal: SellSignal = self.sell_signals.get(signal_id)
            if sell_signal:
                self.sell(signal_id, sell_signal)

    def buy(self, signal_id: UUID, signal: BuySignal) -> None:
        logger.debug(f"Buy signal accepted! Price: {signal.price}")
        signal.accepted = True  # Change signal status as accepted
        price: float = signal.price * self.buy_quantity
        buy_quantity: float = self.buy_quantity - (self.buy_quantity * self.trading_fee)  # 0.1% transaction fee
        transaction: BuyTransaction = BuyTransaction(signal_id, self.symbol, price, buy_quantity, signal.time,
                                                     test=True)
        self.update_stats(True, transaction)

        # Add time of buy and capital to the list of capital over time
        self.capital_over_time.append({"time": signal.time, "capital": self.capital})

    def sell(self, signal_id: UUID, signal: SellSignal) -> None:
        logger.debug(f"Sell signal accepted! Price: {signal.price}")
        signal.accepted = True  # Change signal status to accepted
        buy_transaction: BuyTransaction = self.buy_transactions.get(signal_id)  # Get the corresponding buy transaction

        # We bought 1 BTC for which we actually got 0.999 BTC because of the trading fee
        # At the time, 1 BTC costs xxx €. Now we want to sell those 0.999 BTC that we bought, so we would earn
        # 0.999 BTC * xxx € - transaction fee
        buy_quantity: float = buy_transaction.quantity  # We bought 0.999 BTC
        transaction_cost: float = buy_quantity * signal.price * self.trading_fee  # Costs of the fee
        quantity: float = buy_quantity * signal.price - transaction_cost
        sell_transaction: SellTransaction = SellTransaction(signal_id, self.symbol, buy_quantity, quantity, signal.time,
                                                            test=True)
        self.update_stats(False, sell_transaction, transaction_cost)

        # Add time of sell and new capital to the list of capital over time
        self.capital_over_time.append({"time": signal.time, "capital": self.capital})

    def print_stats(self) -> None:
        print("")
        print(Color.OKCYAN + "========== BACKTEST ==========" + Color.ENDC)
        print("")

        # Backtest config
        print(Color.HEADER + "---Configuration---" + Color.ENDC)
        print(f"Symbol: {self.symbol}")
        print(f"API: {self.api}")
        print(f"Strategy: {self.strategy}")

        # Time period
        start: float = self.market_data.candlestick_data.iloc[0]["time"] / 1000
        start_date: date = date.fromtimestamp(start)
        end: float = self.market_data.candlestick_data.iloc[len(self.market_data.candlestick_data)-1]["time"] / 1000
        end_date: date = date.fromtimestamp(end)
        print(f"Time period: {start_date} - {end_date}")

        print(f"Trading fee: {self.trading_fee * 100}%")
        print(f"Buy quantity: {self.buy_quantity} coins")
        print(f"Starting capital: {self.starting_capital}€")
        print(f"")

        # Test results
        print(Color.HEADER + "---Test Results---" + Color.ENDC)
        print(f"Capital: {round(self.capital, 2)}€")
        print(f"Money spent: {round(self.money_spent, 2)}€")
        print(f"Money earned: {round(self.money_earned, 2)}€")
        print(f"Money spent on transaction fees: {round(self.transaction_costs, 2)}€")
        print(f"Profit: {round(self.money_earned - self.money_spent, 2)}€")
        print("")

        # Buy stats
        print(f"Buy signals created: {len(self.buy_signals)}")
        print(f"Buy signals accepted: {len(self.buy_transactions)}")
        print(f"Buy signals ignored: {len(self.buy_signals) - len(self.buy_transactions)}")
        print(f"Coins bought: {round(self.coins_bought, 2)}")

        if len(self.buy_transactions) != 0:
            avg_buying_price: float = round(self.money_spent / len(self.buy_transactions))
        else:
            avg_buying_price = 0.0
        print(f"Average buying price {avg_buying_price}€")
        print("")

        # Sell stats
        print(f"Sell signals created: {len(self.sell_signals)}")
        print(f"Sell signals accepted: {len(self.sell_transactions)}")
        print(f"Sell signals ignored: {len(self.sell_signals) - len(self.sell_transactions)}")
        print(f"Coins sold: {round(self.coins_sold, 5)}")
        print("")

        # Coins still in our possession
        print(Color.UNDERLINE + "Coins not sold:" + Color.ENDC)
        for signal_id in self.kept_coins:
            transaction: BuyTransaction = self.buy_transactions.get(signal_id)
            print(f"ID: {signal_id} \t Buying price: {round(transaction.price, 2)}€")  # TODO: add current price
        print("")
        print(Color.OKCYAN + "==============================" + Color.ENDC)
        print("")

    def update_stats(self, is_buy: bool, transaction: Union[BuyTransaction, SellTransaction],
                     transaction_cost: float = None):
        """Updates all properties that are necessary for generating backtest stats"""
        if is_buy:
            assert type(transaction) == BuyTransaction
            self.capital -= transaction.price
            self.coins_bought += transaction.quantity
            self.transaction_costs += transaction.price * self.trading_fee
            self.money_spent += transaction.price
            self.kept_coins.append(transaction.transaction_id)  # Add signal id to list of coins in our possession
            self.buy_transactions[transaction.transaction_id] = transaction  # Add to dict of buy transactions
        else:
            assert type(transaction) == SellTransaction
            self.capital += transaction.quantity  # We got xxx euros for selling xxx coins
            self.coins_sold += transaction.price  # We sold xxx coins
            self.transaction_costs += transaction_cost
            self.money_earned += transaction.quantity
            self.kept_coins.remove(transaction.transaction_id)  # Remove signal id from list of coins in our possession
            self.sell_transactions[transaction.transaction_id] = transaction  # Add to dict of sell transactions

    @staticmethod
    def figures_to_html(figures: List[Figure], filename: str = "backtest_dashboard.html"):
        """Creates a single html file from a list of plotly figures"""
        logger.info("Creating backtest dashboard...")
        dashboard: IO = open(filename, 'w')
        dashboard.write("<html><head></head><body>" + "\n")
        for figure in figures:
            inner_html: str = figure.to_html().split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
        dashboard.write("</body></html>" + "\n")

    @staticmethod
    def get_signal_values(signals: dict) -> Tuple[List[datetime], List[float], List[datetime], List[float]]:
        """
        Sorts time and price properties of buy and sell signals into different lists. This is used in order to plot
        accepted signals in different colors than ignored signals
        """
        # Create lists that hold the values of accepted and ignored signals
        accepted_times: List[datetime] = list()
        accepted_prices: List[float] = list()
        ignored_times: List[datetime] = list()
        ignored_prices: List[float] = list()

        # Loop through all of them and sort them into the right lists
        for signal_id, signal in signals.items():
            if signal.accepted:
                accepted_times.append(signal.time)
                accepted_prices.append(signal.price)
            else:
                ignored_times.append(signal.time)
                ignored_prices.append(signal.price)

        # Return all four lists as a tuple
        return accepted_times, accepted_prices, ignored_times, ignored_prices
