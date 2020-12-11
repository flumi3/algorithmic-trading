import os
import sys
import logging_conf  # Init the logger config

from typing import Union, Any
from collections import OrderedDict
from market_data import MarketData
from backtest.backtest import Backtest
from console_app import backtest_terminal
from util import TerminalColors as Color
from strategies.moving_average_strategy import MovingAverageStrategy
from plotly.graph_objs import Figure

tab_str = "    "  # 4 blanks


def display_title_bar() -> None:
    print(Color.OKGREEN + "##########################" + Color.ENDC)
    print(Color.OKGREEN + "#" + tab_str*2 + "Welcome!" + tab_str*2 + "#" + Color.ENDC)
    print(Color.OKGREEN + "##########################" + Color.ENDC)
    print("")


def choose_action() -> int:
    print(Color.BOLD + "What would you like to to?" + Color.ENDC)
    print("")
    print("1) Create new backtest")
    print("99) Exit Program")
    print("")
    try:
        return int(input("Enter number: "))
    except ValueError:
        print("Incorrect Input: Must be a number!\n")


def create_new_backtest() -> None:
    os.system("cls" if os.name == "nt" else "clear")  # Clear console content

    # Choose API
    api: Union[Any, int] = backtest_terminal.choose_api()  # Either the api object (e.g. Binance()) or 99 to quit
    if api == 99:
        return

    # Choose symbol
    symbol: Union[str, int] = backtest_terminal.choose_symbol()  # Either the symbol string or 99 to quit
    if symbol == 99:
        return

    # Choose strategy
    strategy: Union[Any, int] = backtest_terminal.choose_strategy()  # Either the strategy object or 99 to quit
    if strategy == 99:
        return

    # Choose backtest time
    limit: int = backtest_terminal.choose_time()
    if limit == 99:
        return

    # Enter starting capital
    starting_capital: float = backtest_terminal.enter_starting_capital()

    # Enter buy quantity
    buy_quantity: float = backtest_terminal.enter_buy_quantity()

    # Check config and ask whether the user wants to start the backtest
    backtest_terminal.clear_output()
    print(Color.BOLD + "Check selection:" + Color.ENDC)
    print("")
    print(f"API: {api.name}")
    print(f"Symbol: {symbol}")
    print(f"Strategy: {strategy.name}")
    print(f"Starting capital: {starting_capital}")
    print(f"Buy quantity: {buy_quantity}")
    print("")
    user_input = input("Do you want to start the backtest [yes/no]? ")  # TODO: maybe with enter instead of yes/no
    print("")

    if user_input == "yes":
        # ==== Start backtest ==== #
        market_data: MarketData = MarketData(api.get_candlestick_data(symbol, limit=limit))  # Create market data

        # Check which indicators need to be added to the market data (based on the strategy we use)
        if type(strategy) == MovingAverageStrategy:
            market_data.add_sma("slow_sma", 30)

        # Calculate buy and sell signals
        buy_signals: OrderedDict = strategy.calc_buy_signals(market_data.candlestick_data)
        sell_signals: OrderedDict = strategy.calc_sell_signals(market_data.candlestick_data, buy_signals)

        backtest: Backtest = Backtest(symbol, api.name, strategy.name, starting_capital, buy_quantity, api.trading_fee,
                                      market_data, buy_signals, sell_signals)
        backtest.run_backtest()
        candlestick_figure: Figure = backtest.create_candlestick_figure()
        capital_figure: Figure = backtest.create_capital_figure()
        backtest.figures_to_html([candlestick_figure, capital_figure])
        backtest.print_stats()
        input("Press Enter to continue...")


def display_main_menu() -> None:
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        display_title_bar()

        choice: int = choose_action()
        if choice == 1:
            create_new_backtest()
        elif choice == 99:
            sys.exit()


if __name__ == "__main__":
    display_main_menu()
