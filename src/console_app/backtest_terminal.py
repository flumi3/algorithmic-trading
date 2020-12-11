import os

from api.binance import Binance
from strategies.moving_average_strategy import MovingAverageStrategy
from util import TerminalColors as Color
from typing import Union, Any


quit_str: str = "Quit backtest creation"
incorrect_input_str: str = "Incorrect input: Must be a number!"
tab_str: str = "    "  # 4 blanks


def clear_output() -> None:
    if os.name == "nt":
        os.system("cls")  # Windows
    else:
        os.system("clear")  # Unix
    display_title_bar()


def display_title_bar() -> None:
    print(Color.OKGREEN + "#####################################" + Color.ENDC)
    print(Color.OKGREEN + "#" + tab_str*2 + "Create New Backtest" + tab_str*2 + "#" + Color.ENDC)
    print(Color.OKGREEN + "#####################################" + Color.ENDC)
    print("")


def choose_api() -> Union[Any, int]:
    while True:
        clear_output()
        print(Color.BOLD + "Choose API:" + Color.ENDC)
        print("")
        print("1) Binance")
        print("99) " + quit_str)
        print("")
        try:
            user_input = int(input("Enter number: "))
        except ValueError:
            print(incorrect_input_str)
        else:
            if user_input == 1:
                api: Binance = Binance()
                return api
            elif user_input == 99:
                return 99
            else:
                print("Incorrect input. Try again!")


def choose_symbol() -> Union[str, int]:
    while True:
        clear_output()
        print(Color.BOLD + "Choose symbol:" + Color.ENDC)
        print("")
        print("1) Bitcoin/Euro")
        print("99) " + quit_str)
        print("")
        try:
            user_input = int(input("Enter number: "))
        except ValueError:
            print(incorrect_input_str)
        else:
            if user_input == 1:
                return "BTCEUR"
            elif user_input == 99:
                return 99
            else:
                print("Incorrect input. Try again!")


def choose_strategy():
    while True:
        clear_output()
        print(Color.BOLD + "Choose strategy:" + Color.ENDC)
        print("")
        print("1) Moving Average Strategy")
        print("99) " + quit_str)
        print("")
        try:
            user_input = int(input("Enter number: "))
        except ValueError:
            print(incorrect_input_str)
        else:
            if user_input == 1:
                strategy: MovingAverageStrategy = MovingAverageStrategy()
                return strategy
            elif user_input == 99:
                return 99
            else:
                print("Incorrect input. Try again!")


def choose_time() -> int:
    while True:
        clear_output()
        print(Color.BOLD + "Choose time of backtest:" + Color.ENDC)
        print("")
        print("1) One month")
        print("2) Three months")
        print("3) Six months")
        print("4) One year")
        print("")
        try:
            user_input: int = int(input("Enter number: "))
        except ValueError:
            print(incorrect_input_str)
        else:
            if user_input == 1:
                return 720  # 30 days * 24h = 720 candles
            elif user_input == 2:
                return 2160
            elif user_input == 3:
                return 4320
            elif user_input == 4:
                return 8640
            elif user_input == 99:
                return 99
            else:
                print("Incorrect input. Try again!")


def enter_starting_capital():
    while True:
        clear_output()
        try:
            return float(input("Enter starting capital: "))
        except ValueError:
            print(incorrect_input_str)


def enter_buy_quantity():
    while True:
        clear_output()
        try:
            return float(input("Enter buy quantity: "))
        except ValueError:
            print(incorrect_input_str)

# Choose API

# Choose currency

# Choose strategy

# Enter starting capital

# Enter buy quantity

# Enter start date (optional)

# Enter end date (optional)

# Enter name?
