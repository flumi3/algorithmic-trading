from typing import List, Union, Tuple, OrderedDict

from plotly.graph_objs import Figure
from prompt_toolkit import prompt

from api.binance import Binance
from backtest.backtest import Backtest
from cli.util import display_header, choose_option, print_bold
from cli.validator import FloatValidator, YesNoValidator
from market_data import MarketData
from strategies.moving_average_strategy import MovingAverageStrategy

tab_str = "    "  # 4 blanks
quit_str: str = "Quit backtest creation"

backtest_header: str = "#####################################\n" \
                       + "#" + tab_str*2 + "Create New Backtest" + tab_str*2 + "#\n" \
                       + "#####################################"


def choose_api() -> Union[Binance, int]:
    display_header(backtest_header)
    api_title = "Choose API:"
    api_options: List[str] = ["1) Binance", "99) " + quit_str]
    api_choice: int = choose_option(api_title, api_options)

    if api_choice == 1:
        return Binance()
    elif api_choice == 99:
        return 99


def choose_symbol() -> Union[str, int]:
    display_header(backtest_header)
    symbol_title = "Choose symbol:"
    symbol_options: List[str] = ["1) Bitcoin/Euro", "99) " + quit_str]
    symbol_choice: int = choose_option(symbol_title, symbol_options)

    if symbol_choice == 1:
        return "BTCEUR"
    elif symbol_choice == 99:
        return 99


def choose_strat() -> Union[MovingAverageStrategy, int]:
    display_header(backtest_header)
    strat_title = "Choose strategy:"
    strat_options: List[str] = ["1) Moving Average Strategy", "99) " + quit_str]
    strat_choice: int = choose_option(strat_title, strat_options)

    if strat_choice == 1:
        return MovingAverageStrategy()
    elif strat_choice == 99:
        return 99


def choose_time_frame() -> Tuple[int, str]:
    display_header(backtest_header)
    time_title = "Choose time frame:"
    time_options: List[str] = ["1) One month", "2) Three months", "3) Six months", "4) One year", "99) " + quit_str]
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


def create_backtest() -> None:
    display_header(backtest_header)

    # Backtest config
    api: Union[Binance] = choose_api()
    if api == 99:
        return
    symbol: str = choose_symbol()
    if symbol == 99:
        return
    strategy: Union[MovingAverageStrategy] = choose_strat()
    if strategy == 99:
        return
    kline_limit, time_frame_name = choose_time_frame()  # kline_limit = int, time_frame_name = str
    if kline_limit == 99:
        return
    display_header(backtest_header)
    starting_capital: float = float(prompt("Enter starting capital: ", validator=FloatValidator()))
    display_header(backtest_header)
    buy_quantity: float = float(prompt("Enter buy quantity: ", validator=FloatValidator()))

    # Check config and ask whether the user wants to start the backtest
    display_header(backtest_header)
    print_bold("Check configuration: ")
    print("")
    print(f"API: {api.base}")
    print(f"Symbol: {symbol}")
    print(f"Strategy: {strategy.name}")
    print(f"Time frame: {time_frame_name}")
    print(f"Starting capital: {starting_capital}")
    print(f"Buy quantity: {buy_quantity}")
    print("")
    user_input: str = prompt("Do you want to start the backtest? [y/n] ", validator=YesNoValidator())
    print("")

    if user_input == "y":
        # Create market data
        market_data: MarketData = MarketData(api.get_candlestick_data(symbol, limit=kline_limit))

        # Check which indicators need to be added to the market data (based on the strategy we use)
        if type(strategy) == MovingAverageStrategy:
            market_data.add_sma("slow_sma", 30)

        # Calculate buy and sell signals
        buy_signals: OrderedDict = strategy.calc_buy_signals(market_data.candlestick_data)
        sell_signals: OrderedDict = strategy.calc_sell_signals(market_data.candlestick_data, buy_signals)

        # Create backtest
        backtest: Backtest = Backtest(symbol, api.base, strategy.name, starting_capital, buy_quantity, api.trading_fee,
                                      market_data, buy_signals, sell_signals)
        backtest.run_backtest()

        # Plotting stuff and statistics
        candlestick_figure: Figure = backtest.create_candlestick_figure()
        capital_figure: Figure = backtest.create_capital_figure()
        backtest.figures_to_html([candlestick_figure, capital_figure])
        backtest.print_stats()
        input("Press Enter to continue...")
    elif user_input == "n":
        return
