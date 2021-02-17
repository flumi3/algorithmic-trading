import sys
import logging_conf  # Init the logger config (do not remove)

from prompt_toolkit import prompt
from typing import List, Union
from api.binance import Binance
from backtest.backtest import Backtest
from bot import Bot
from bot_runner import BotRunner
from cli.choices import choose_api, choose_symbol, choose_strat, choose_time_frame
from cli.headers import HEADER_NEW_BACKTEST, HEADER_WELCOME, HEADER_NEW_BOT, HEADER_DISPLAY_BOTS
from cli.cli_util import choose_option, display_header, print_bold
from cli.validators import FloatValidator, YesNoValidator
from strategies.moving_average_strategy import MovingAverageStrategy
from util import TerminalColors


class CommandLineInterface:

    def __init__(self, bot_runner: BotRunner) -> None:
        self.bot_runner: BotRunner = bot_runner

    def display_main_menu(self) -> None:
        """Displays the main menu and lets the user choose what he would like to do."""

        while True:
            # Get user choice
            title: str = "What would you like to do?"
            options: List[str] = [
                "1) Create new backtest",
                "2) Create new trading bot",
                "3) Display trading bots",
                "99) Exit program"
            ]
            choice: int = choose_option(title, options, HEADER_WELCOME)

            # Check what the user chose to do
            if choice == 1:
                self.create_backtest()
            elif choice == 2:
                self.create_bot()
            elif choice == 3:
                self.display_trading_bots()
            elif choice == 99:
                sys.exit()

    def create_backtest(self) -> None:
        # Backtest config
        api: Union[Binance] = choose_api(HEADER_NEW_BACKTEST)
        if api == 99:
            return
        symbol: str = choose_symbol(HEADER_NEW_BACKTEST)
        if symbol == 99:
            return
        strategy: Union[MovingAverageStrategy] = choose_strat(HEADER_NEW_BACKTEST)
        if strategy == 99:
            return
        kline_limit, time_frame_name = choose_time_frame(HEADER_NEW_BACKTEST)
        if kline_limit == 99:
            return
        starting_capital: float = self.__get_starting_capital(HEADER_NEW_BACKTEST)
        buy_quantity: float = self.__get_buy_quantity(HEADER_NEW_BACKTEST)

        # Check config and ask whether the user wants to start the backtest
        display_header(HEADER_NEW_BACKTEST)
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
            # Create backtest
            backtest: Backtest = Backtest(symbol, api, strategy, starting_capital, buy_quantity, kline_limit)
            backtest.run()
            input("Press Enter to continue...")
        elif user_input == "n":
            return

    def create_bot(self) -> None:
        display_header(HEADER_NEW_BOT)

        # Ask for name of bot
        name: str = ""
        while name == "":
            display_header(HEADER_NEW_BOT)
            name = prompt("Enter name: ")

        # Get symbol choice
        symbol: str = choose_symbol(HEADER_NEW_BOT)
        if symbol == 99:
            return
        api: Union[Binance] = choose_api(HEADER_NEW_BOT)
        if api == 99:
            return  # TODO: check whether we have access to the binance account
        strategy: Union[MovingAverageStrategy] = choose_strat(HEADER_NEW_BOT)
        if strategy == 99:
            return

        # Give user the option to cap the capital that the bot can use
        # E.g. we have 600€ capital on our Binance account. Then we can let the bot use only 200€ of those 600€.
        starting_capital: float = self.__get_starting_capital(HEADER_NEW_BOT)
        buy_quantity: float = self.__get_buy_quantity(HEADER_NEW_BOT)

        # Let user enter description
        display_header(HEADER_NEW_BOT)
        description: str = prompt("Enter description (optional): ")

        display_header(HEADER_NEW_BOT)
        print_bold("Check configuration: ")
        print("")
        print(f"Name: {name}")
        print(f"Symbol: {symbol}")
        print(f"API: {api.base}")
        print(f"Strategy: {strategy.name}")
        print(f"Starting capital: {starting_capital}")
        print(f"Buy quantity: {buy_quantity}")
        print(f"Description: {description}")
        print("")
        user_input: str = prompt("Do you want to start the backtest? [y/n] ", validator=YesNoValidator())
        print("")

        if user_input == "y":
            # Create bot
            bot: Bot = Bot(name, symbol, api, strategy, starting_capital, buy_quantity, description)
            bot_id: int = self.bot_runner.add_bot(bot)
        elif user_input == "n":
            return

    def display_trading_bots(self) -> None:
        display_header(HEADER_DISPLAY_BOTS)
        print_bold("ID\t\tNAME\t\tSYMBOL\t\tSTATUS")
        print("-----------------------------------------------------------")
        for bot_id, bot in self.bot_runner.bots.items():
            if bot.status == bot.STATUS_INIT:
                status_text: str = TerminalColors.OKCYAN + bot.status + TerminalColors.ENDC
            elif bot.status == bot.STATUS_RUNNING:
                status_text: str = TerminalColors.OKGREEN + bot.status + TerminalColors.ENDC
            elif bot.status == bot.STATUS_PAUSED:
                status_text: str = TerminalColors.WARNING + bot.status + TerminalColors.ENDC
            elif bot.status == bot.STATUS_ABORTED:
                status_text: str = TerminalColors.FAIL + bot.status + TerminalColors.ENDC
            else:
                status_text: str = bot.status
            print(f"{bot_id}\t\t{bot.name}\t\t{bot.symbol}\t\t{status_text}")
        print("")
        input("Press Enter to go back...")

    @staticmethod
    def __get_starting_capital(header) -> float:
        user_input: str = ""
        while user_input == "":
            display_header(header)
            user_input = prompt("Enter starting capital: ", validator=FloatValidator())
        if header == HEADER_NEW_BOT:
            # TODO: check whether our account has enough capital
            pass
        return float(user_input)

    @staticmethod
    def __get_buy_quantity(header) -> float:
        # TODO: how to handle quantity filters? Because you have to specify a quantity that is allowed by the platform
        user_input: str = ""
        while user_input == "":
            display_header(header)
            user_input = prompt("Enter buy quantity: ", validator=FloatValidator())
        return float(user_input)
