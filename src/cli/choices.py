from typing import Union, List, Tuple

from api.binance import Binance
from cli.cli_util import display_header, choose_option
from strategies.moving_average_strategy import MovingAverageStrategy


def choose_api(header: str) -> Union[Binance, int]:
    display_header(header)
    api_title: str = "Choose API:"
    api_options: List[str] = ["1) Binance", "99) Quit"]
    api_choice: int = choose_option(api_title, api_options)

    if api_choice == 1:
        return Binance()
    elif api_choice == 99:
        return 99


def choose_symbol(header: str) -> Union[str, int]:
    display_header(header)
    symbol_title: str = "Choose symbol:"
    symbol_options: List[str] = ["1) Bitcoin/Euro", "2) Ethereum/Euro", "3) Litecoin/Euro", "99) Quit"]
    symbol_choice: int = choose_option(symbol_title, symbol_options)

    if symbol_choice == 1:
        return Binance.SYMBOL_BITCOIN_EURO
    if symbol_choice == 2:
        return Binance.SYMBOL_ETHEREUM_EURO
    if symbol_choice == 3:
        return Binance.SYMBOL_LITECOIN_EURO
    elif symbol_choice == 99:
        return 99


def choose_strat(header: str) -> Union[MovingAverageStrategy, int]:
    display_header(header)
    strat_title: str = "Choose strategy:"
    strat_options: List[str] = ["1) Moving Average Strategy", "99) Quit"]
    strat_choice: int = choose_option(strat_title, strat_options)

    if strat_choice == 1:
        return MovingAverageStrategy()
    elif strat_choice == 99:
        return 99


def choose_time_frame(header: str) -> Tuple[int, str]:
    display_header(header)
    time_title: str = "Choose time frame:"
    time_options: List[str] = ["1) One month", "2) Three months", "3) Six months", "4) One year", "99) Quit"]
    time_choice: int = choose_option(time_title, time_options)

    if time_choice == 1:
        return 720, "One month"  # 30 days * 24h = 720 candles
    elif time_choice == 2:
        return 2160, "Three months"
    elif time_choice == 3:
        return 4320, "Six months"
    elif time_choice == 4:
        return 8640, "One year"
    elif time_choice == 99:
        return 99, ""
