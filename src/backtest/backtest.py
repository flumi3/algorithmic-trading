import logging

from datetime import datetime
from logging import Logger
from plotly.graph_objs import Candlestick, Layout, Figure, Scatter
from plotly.offline import plot
from typing import List, Tuple, Dict
from collections import OrderedDict
from market_data import MarketData
from indicators import SmoothedMovingAverage
from backtest.signals import BuySignal, SellSignal
from uuid import UUID
from pandas import DataFrame
from transactions import BuyTransaction, SellTransaction

logger: Logger = logging.getLogger(__name__)


class Backtest:

    def __init__(self, symbol: str, api: str, strategy: str, capital: float, buy_quantity: float,
                 transaction_fee: float,  start_date: datetime, end_date: datetime, market_data: MarketData,
                 sell_signals: OrderedDict = None,
                 buy_signals: OrderedDict = None) -> None:
        # Backtest configuration
        self.symbol = symbol
        self.api: str = api
        self.strategy: str = strategy
        self.starting_capital: float = capital
        self.buy_quantity: float = buy_quantity
        self.trading_fee: float = transaction_fee
        self.start_date: datetime = start_date
        self.end_date: datetime = end_date
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

        times: List[datetime] = self.market_data.candlestick_data["time"].tolist()
        capitals: List[float] = [self.capital for i in range(len(times))]
        self.capitals_df: DataFrame = DataFrame(list(zip(times, capitals)), columns=["time", "capital"])

    def plot_candlestick_chart(self, plot_title: str) -> None:
        """Plots a candlestick chart"""
        logger.info("Plotting candlestick chart...")

        # Access candlestick data frame which gets hold by the market data object
        df = self.market_data.candlestick_data

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
            values: tuple = self.get_signal_values(self.buy_signals)
            accepted_times: datetime = values[0]
            accepted_prices: float = values[1]
            ignored_times: datetime = values[2]
            ignored_prices: float = values[3]

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
            values: tuple = self.get_signal_values(self.sell_signals)
            accepted_times: datetime = values[0]
            accepted_prices: float = values[1]
            ignored_times: datetime = values[2]
            ignored_prices: float = values[3]

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
                "title": "Price"
            }
        )
        # Create figure and plot it
        figure: Figure = Figure(data=data, layout=layout)
        plot(figure, filename=plot_title + ".html")

    def plot_capital_chart(self) -> None:
        capital_line: Scatter = Scatter(
            x=self.capitals_df["time"],
            y=self.capitals_df["capital"],
            name="Capital",
            line=dict(color="rgba(0, 0, 255, 1)")
        )
        layout: Layout = Layout(
            xaxis={
                "title": "Capital over time",
                "rangeslider": {"visible": True},
                "type": "date"
            },
            yaxis={
                "fixedrange": False,
                "title": "Capital"
            }
        )
        figure: Figure = Figure(capital_line, layout=layout)
        plot(figure, filename="capital.html")

    def run_backtest(self) -> None:
        logger.info("Running backtest...")

        for buy_signal_id, buy_signal in self.buy_signals.items():
            # Loop through all coins that we have not sold yet and check if we can sell them
            for signal_id in self.kept_coins:
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

        # # Check sell options for all coins we have not sold yet
        # for signal_id in self.kept_coins:
        #     sell_signal: SellSignal = self.sell_signals.get(signal_id)
        #     if sell_signal:
        #         self.sell(signal_id, sell_signal)

        self.print_stats()

    def buy(self, signal_id: UUID, signal: BuySignal) -> None:
        signal.accepted = True  # Change signal status as accepted
        price: float = signal.price * self.buy_quantity
        buy_quantity: float = self.buy_quantity - (self.buy_quantity * self.trading_fee)  # 0.1% transaction fee
        transaction: BuyTransaction = BuyTransaction(signal_id, self.symbol, price, buy_quantity, signal.time,
                                                     test=True)
        # Update stats
        self.capital -= transaction.price
        self.coins_bought += transaction.quantity
        self.transaction_costs += transaction.price * self.trading_fee
        self.money_spent += transaction.price
        self.kept_coins.append(transaction.transaction_id)  # Add signal id to list of coins in our possession
        self.buy_transactions[transaction.transaction_id] = transaction  # Add to dict of buy transactions
        logger.debug(f"Buy signal accepted! Price: {signal.price}")

        # Change all capital values starting from this exact buying time to the current capital (for the capital chart)
        self.capitals_df.loc[self.capitals_df["time"] >= signal.time, "capital"] = self.capital

    def sell(self, signal_id: UUID, signal: SellSignal) -> None:
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
        # Update stats
        self.capital += sell_transaction.quantity  # We got xxx euros for selling xxx coins
        self.coins_sold += sell_transaction.price  # We sold xxx coins
        self.transaction_costs += transaction_cost
        self.money_earned += sell_transaction.quantity
        self.kept_coins.remove(signal_id)  # Remove signal id from list of coins in our possession
        self.sell_transactions[sell_transaction.transaction_id] = sell_transaction  # Add to dict of sell transactions
        logger.debug(f"Sell signal accepted! Price: {signal.price}")

        # Change all capital values starting form this exact selling time to the current capital (for the capital chart)
        self.capitals_df.loc[self.capitals_df["time"] >= signal.time, "capital"] = self.capital

    def print_stats(self) -> None:
        print("========== BACKTEST ==========")

        # Backtest config
        print("---Configuration---")
        print(f"Symbol: {self.symbol}")
        print(f"API: {self.api}")
        print(f"Strategy: {self.strategy}")
        print(f"Time period: {self.start_date} - {self.end_date}")

        print(f"Transaction fee: {self.trading_fee}")
        print(f"Buy Quantity: {self.buy_quantity}")
        print(f"Starting capital: {self.starting_capital}€")
        print(f"")

        # Test results
        print("---Test Results---")
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
        print(f"Average buying price {round(self.money_spent / len(self.buy_transactions))}€")
        print("")

        # Sell stats
        print(f"Sell signals created: {len(self.sell_signals)}")
        print(f"Sell signals accepted: {len(self.sell_transactions)}")
        print(f"Sell signals ignored: {len(self.sell_signals) - len(self.sell_transactions)}")
        print(f"Coins sold: {round(self.coins_sold, 5)}")
        print("")

        # Coins still in our possession
        print("Coins not sold:")
        for signal_id in self.kept_coins:
            buy_signal: BuySignal = self.buy_signals.get(signal_id)
            print(f"ID: {signal_id} \t Price: {buy_signal.price}€")

        print("==============================")

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
