import logging
import os

from datetime import datetime, date
from logging import Logger
from pathlib import Path
from plotly.graph_objs import Candlestick, Layout, Figure, Scatter
from typing import List, Tuple, Union, Dict
from collections import OrderedDict
from api.binance import Binance
from indicators import SmoothedMovingAverage
from buy_signal import BuySignal
from uuid import UUID
from pandas import DataFrame
from strategies.moving_average_strategy import MovingAverageStrategy
from transactions import BuyTransaction, SellTransaction
from util import TerminalColors as Color, get_project_root

logger: Logger = logging.getLogger("__main__")


class Backtest:

    def __init__(self, symbol: str, api: Union[Binance], strategy: Union[MovingAverageStrategy], capital: float,
                 buy_quantity: float, kline_limit: int) -> None:
        # Backtest configuration
        self.symbol = symbol
        self.api: Union[Binance] = api
        self.strategy: Union[MovingAverageStrategy] = strategy
        self.starting_capital: float = capital
        self.buy_quantity: float = buy_quantity
        self.kline_limit: int = kline_limit
        # Statistic properties
        self.money_spent: float = 0
        self.money_earned: float = 0
        self.transaction_costs: float = 0  # Sum of the money that got lost in transaction fees
        self.coins_bought: float = 0
        self.coins_sold: float = 0
        self.coins_in_possession: float = 0
        # Other
        self.capital: float = capital
        self.buy_signals: OrderedDict[UUID, BuySignal] = OrderedDict()
        self.buy_transactions: OrderedDict[UUID, BuyTransaction] = OrderedDict()
        self.sell_transactions: OrderedDict[UUID, SellTransaction] = OrderedDict()
        self.kept_coins: List[UUID] = list()  # List of coins that we have not sold yet
        self.capital_over_time: List[Dict[str, Union[UUID, float]]] = list()  # Represents our capital over the time
        self.candlestick_df: DataFrame = DataFrame()
        self.dashboard_dir: str = os.path.join(get_project_root(), "dashboards/" + self.strategy.name.replace(" ", "_")
                                               + "/" + self.symbol)

    def run(self) -> None:
        logger.info("Running backtest...")

        # Init some necessary properties to run the backtest
        self.candlestick_df: DataFrame = self.api.get_candlestick_data(symbol=self.symbol, limit=self.kline_limit)
        self.strategy.add_indicators(self.candlestick_df, column_name="close")
        self.capital_over_time.append({"time": self.candlestick_df["time"][0], "capital": self.capital})

        profit_target_price: float = -1  # Price of our profit goal
        stop_loss_price: float = -1  # Price of our stop loss
        for index, row in self.candlestick_df.iterrows():
            # Check whether we can buy
            close_price: float = getattr(row, "close")
            time: datetime = getattr(row, "time")
            buy_signal: Union[BuySignal, bool] = self.strategy.check_buy_condition(close_price, time, row)
            if buy_signal:
                self.buy_signals[buy_signal.signal_id] = buy_signal
                if self.capital >= close_price:
                    self.__buy(buy_signal)
                    if profit_target_price == -1 and stop_loss_price == -1:
                        profit_target_price = close_price * self.strategy.profit_target
                        stop_loss_price = close_price * self.strategy.stop_loss_target

            # Check whether we can sell
            for coin_id in self.kept_coins.copy():  # Copy because we modify the dict while iterating
                low_price: float = getattr(row, "low")  # For selling, we inspect the lowest price within the candle
                if low_price <= stop_loss_price:
                    # If price hits the stop loss -> sell
                    self.__sell(stop_loss_price, time)
                    # Reset profit target price and stop loss price because we have sold all coins
                    profit_target_price = -1
                    stop_loss_price = -1
                elif close_price >= profit_target_price != -1:
                    # If price surpassed our profit target, set new profit and stop loss target
                    profit_target_price = close_price * self.strategy.profit_target
                    stop_loss_price = close_price * self.strategy.stop_loss_target

        self.__create_folder_structure()
        cs_figure: Figure = self.__create_candlestick_figure()
        capital_figure: Figure = self.__create_capital_figure()
        html_figures: str = self.__figures_to_html([cs_figure, capital_figure])
        html_stats: str = self.__stats_to_html()
        self.create_html_dashboard(html_figures, html_stats)
        self.print_stats()

    def print_stats(self) -> None:
        current_price: float = self.api.get_current_price(self.symbol)
        print("")
        print(Color.OKCYAN + "========== BACKTEST ==========" + Color.ENDC)
        print("")
        print(f"Find your dashboard at {self.dashboard_dir}")
        print("")

        # Backtest config
        print(Color.HEADER + "---Configuration---" + Color.ENDC)
        print(f"Symbol: {self.symbol}")
        print(f"API: {self.api.base}")
        print(f"Strategy: {self.strategy.name}")

        # Time period
        date_format: str = "%d.%m.%Y"
        start: float = self.candlestick_df.iloc[0]["time"] / 1000
        start_date: str = date.fromtimestamp(start).strftime(date_format)
        end: float = self.candlestick_df.iloc[len(self.candlestick_df)-1]["time"] / 1000
        end_date: str = date.fromtimestamp(end).strftime(date_format)
        print(f"Time period: {start_date} - {end_date}")

        print(f"Trading fee: {self.api.trading_fee * 100}%")
        print(f"Buy quantity: {self.buy_quantity} coins")
        print(f"Starting capital: {self.starting_capital}€")
        print(f"")

        # Test results
        print(Color.HEADER + "---Test Results---" + Color.ENDC)
        print(f"Capital: {round(self.capital, 2)}€")
        print(f"Money spent: {round(self.money_spent, 2)}€")
        print(f"Money earned: {round(self.money_earned, 2)}€")
        print(f"Money spent on transaction fees: {round(self.transaction_costs, 2)}€")
        profit: float = self.money_earned - self.money_spent
        print(f"Profit: {round(profit, 2)}€")
        print("")

        # Buy stats
        average_buying_price, average_selling_price = self.__get_average_transaction_prices()
        print(f"Buy signals created: {len(self.buy_signals)}")
        print(f"Buy signals accepted: {len(self.buy_transactions)}")
        print(f"Buy signals ignored: {len(self.buy_signals) - len(self.buy_transactions)}")
        print(f"Coins bought: {round(self.coins_bought, 5)}")

        print(f"Average buying price {average_buying_price}€")
        print("")

        # Sell stats
        print(f"Coins sold: {round(self.coins_sold, 5)}")
        print(f"Average selling price: {round(average_selling_price, 2)}€")
        print(f"Coins not sold: {round(self.coins_in_possession, 5)}")
        print("")
        turnover: float = self.coins_in_possession * current_price * (1 - self.api.trading_fee)
        print(f"Profit when selling all coins now: {round(turnover + profit, 2)}€")

        print("")
        print(Color.OKCYAN + "==============================" + Color.ENDC)
        print("")

    def create_html_dashboard(self, html_figures: str, html_stats: str) -> None:
        logger.info("Creating backtest dashboard...")
        # Create dashboard name/path based on the date of the backtest
        timestamp: str = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename: str = self.symbol + "_" + timestamp + ".html"
        path: str = os.path.join(self.dashboard_dir, filename)

        # Create headline
        html_headline: str = f"""
        <p><br /></p>
        <h1 style="text-align: center;"><span style="font-size: 48px; font-family: Arial, Helvetica, sans-serif;">Backtest Dashboard</span></h1>
        <h1 style="text-align: center;"><span style="font-size: 24px; font-family: Arial, Helvetica, sans-serif;">{date.today().strftime("%d.%m.%Y")}</span></h1>
        """

        # Write content to html file
        with open(path, "w") as dashboard:
            dashboard.write("<html><head></head><body>" + "\n")
            dashboard.write(html_headline)  # add headline
            dashboard.write(html_figures)  # add plots
            dashboard.write(html_stats)  # add backtest stats
            dashboard.write("</body></html>" + "\n")

    def __buy(self, signal: BuySignal) -> None:
        logger.debug(f"Buy signal accepted! Price: {signal.price}")
        signal.accepted = True  # Change signal status as accepted
        price: float = signal.price * self.buy_quantity
        buy_quantity: float = self.buy_quantity - (self.buy_quantity * self.api.trading_fee)  # 0.1% transaction fee
        transaction: BuyTransaction = BuyTransaction(signal.signal_id, self.symbol, price, buy_quantity, signal.time)
        self.__update_stats(True, transaction)
        self.kept_coins.append(signal.signal_id)
        self.coins_in_possession += buy_quantity
        # Add time of buy and capital to the list of capital over time
        self.capital_over_time.append({"time": signal.time, "capital": self.capital})

    def __sell(self, price: float, time: datetime) -> None:
        for coin_id in self.kept_coins.copy():
            logger.debug(f"Selling coin '{coin_id}' for {price}")
            buy_transaction: BuyTransaction = self.buy_transactions.get(coin_id)  # Get corresponding buy transaction
            # We bought 1 BTC for which we actually got 0.999 BTC because of the trading fee
            # At the time, 1 BTC costs xxx €. Now we want to sell those 0.999 BTC that we bought, so we would earn
            # 0.999 BTC * xxx € - transaction fee
            sell_quantity: float = buy_transaction.buy_quantity  # We bought 0.999 BTC
            transaction_cost: float = sell_quantity * price * self.api.trading_fee  # Costs of the fee
            sell_price: float = sell_quantity * price - transaction_cost  # Price we get in Euros
            sell_transaction: SellTransaction = SellTransaction(coin_id, self.symbol, sell_quantity, sell_price, time)
            self.__update_stats(False, sell_transaction, transaction_cost)
            self.kept_coins.remove(coin_id)
            self.coins_in_possession -= sell_quantity
            # Add time of sell and new capital to the list of capital over time
            self.capital_over_time.append({"time": time, "capital": self.capital})

    def __create_candlestick_figure(self) -> Figure:
        """Creates a candlestick figure that visualizes the market data of the backtest including the signals"""
        df = self.candlestick_df  # Access candlestick frame which gets hold by the market data object

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
        for indicator in self.strategy.indicators:
            # Smoothed moving average
            if type(indicator) == SmoothedMovingAverage:
                sma: Scatter = Scatter(
                    x=df["time"],
                    y=df[indicator.name],
                    name=indicator.name,
                    line=dict(color="rgba(255, 207, 102, 1)")
                )
                data.append(sma)
            # Continue with other indicator types for plotting:
            # if type(indicator) == Indicator...

        # Plot buy signals if we have some
        if self.buy_signals:
            # Create lists that hold the values of accepted and ignored signals
            accepted_times: List[datetime] = list()
            accepted_prices: List[float] = list()
            ignored_times: List[datetime] = list()
            ignored_prices: List[float] = list()
            # Loop through all of them and sort them into the right lists
            for signal_id, signal in self.buy_signals.items():
                if signal.accepted:
                    accepted_times.append(signal.time)
                    accepted_prices.append(signal.price)
                else:
                    ignored_times.append(signal.time)
                    ignored_prices.append(signal.price)

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

        # Plot points where we sold coins
        if self.sell_transactions:
            times: List[datetime] = list()
            prices: List[float] = list()
            for trans_id, trans in self.sell_transactions.items():
                times.append(trans.time)
                prices.append(trans.sell_price / self.buy_quantity)
            sells: Scatter = Scatter(
                x=times,
                y=prices,
                name="Sell Orders",
                mode="markers",
                line=dict(color="rgba(139, 69, 19, 1)")  # Brown
            )
            data.append(sells)

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

    def __create_capital_figure(self) -> Figure:
        # Get last entry of our market data and add its time and our current capital to the dict so the chart will not
        # end at the time of the last transaction
        last_time: datetime = self.candlestick_df["time"].iloc[-1]
        self.capital_over_time.append({"time": last_time, "capital": self.capital})
        capitals_df: DataFrame = DataFrame(self.capital_over_time, columns=["time", "capital"])
        capitals_df = capitals_df.sort_values(by=["time"])

        """Creates a plotly figure that represents our capital over the time of the backtest"""
        capital_line: Scatter = Scatter(
            x=capitals_df["time"],
            y=capitals_df["capital"],
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
                "title": "Capital in Euro"
            }
        )
        figure: Figure = Figure(capital_line, layout=layout)
        return figure

    def __update_stats(self, is_buy: bool, transaction: Union[BuyTransaction, SellTransaction],
                       transaction_cost: float = None):
        """Updates all properties that are necessary for generating backtest stats"""
        if is_buy:
            assert type(transaction) == BuyTransaction
            self.capital -= transaction.buy_price
            self.coins_bought += transaction.buy_quantity
            self.transaction_costs += transaction.buy_quantity * self.api.trading_fee
            self.money_spent += transaction.buy_price
            self.buy_transactions[transaction.transaction_id] = transaction  # Add to dict of buy transactions
        else:
            assert type(transaction) == SellTransaction
            self.capital += transaction.sell_price  # We got xxx euros for selling xxx coins
            self.coins_sold += transaction.sell_quantity  # We sold xxx coins
            self.transaction_costs += transaction_cost
            self.money_earned += transaction.sell_price
            self.sell_transactions[transaction.transaction_id] = transaction  # Add to dict of sell transactions

    def __create_folder_structure(self):
        """
        Creates the folder structure in which all executed backtest dashboards are stored.

        The symbol structure goes like this: .../Algorithmic-Trading/dashboards/<strategy name>/<symbol>/
        """
        logger.debug("Creating backtest folder structure...")
        Path(self.dashboard_dir).mkdir(parents=True, exist_ok=True)

    def __get_average_transaction_prices(self) -> Tuple[float, float]:
        if self.buy_transactions:
            average_buying_price: float = round(self.money_spent / len(self.buy_transactions), 2)
        else:
            average_buying_price = 0.0
        if self.sell_transactions:
            average_selling_price: float = round(self.money_earned / len(self.sell_transactions), 2)
        else:
            average_selling_price = 0.0
        return average_buying_price, average_selling_price

    def __stats_to_html(self) -> str:
        average_buying_price_var, average_selling_price_var = self.__get_average_transaction_prices()
        symbol_var = self.symbol
        api_var = self.api.base
        strategy_var = self.strategy.name
        trading_fee_var = self.api.trading_fee * 100
        buy_quantity_var = self.buy_quantity
        starting_capital_var = self.starting_capital
        capital_var = round(self.capital, 2)
        money_spent_var = round(self.money_spent, 2)
        money_earned_var = round(self.money_earned, 2)
        transaction_fees_var = round(self.transaction_costs, 2)
        profit_var = round(self.money_earned - self.money_spent, 2)
        buy_signals_created_var = len(self.buy_signals)
        buy_signals_accepted_var = len(self.buy_transactions)
        buy_signals_ignored_var = len(self.buy_signals) - len(self.buy_transactions)
        coins_bought_var = round(self.coins_bought, 5)
        coins_sold_var = round(self.coins_sold, 5)
        coins_not_sold_var = round(self.coins_in_possession, 5)
        turnover: float = self.coins_in_possession * self.api.get_current_price(self.symbol) * (1-self.api.trading_fee)
        profit_sell_all_var = round(profit_var + turnover, 2)

        # Get html code skeleton from file
        path: str = os.path.join(get_project_root(), "src/backtest/backtest_stats.html")
        f = open(path, "r")
        html_code: str = f.read()

        # Substitute variables in html code with local variables from here
        html_code = html_code.format(**locals())
        return html_code

    @staticmethod
    def __figures_to_html(figures: List[Figure]) -> str:
        """Creates a single HTML file from a list of plotly figures"""
        logger.debug("Converting plot figures to html code...")
        inner_html: str = ""
        for figure in figures:
            inner_html = inner_html + figure.to_html().split('<body>')[1].split('</body>')[0]
        return inner_html
