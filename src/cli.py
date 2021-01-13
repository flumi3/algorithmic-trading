import sys
from typing import List

from cli.backtest_terminal import create_backtest
from cli.util import choose_option, clear_output, display_header

tab_str = "    "  # 4 blanks
welcome_header: str = "##########################\n" \
                      + "#" + tab_str * 2 + "Welcome!" + tab_str * 2 + "#\n" \
                      + "##########################"


def display_main_menu() -> None:
    """Displays the main menu and lets the user choose what he would like to do."""

    while True:
        clear_output()
        display_header(welcome_header)

        # Get user choice
        title: str = "What would you like to do?"
        options: List[str] = [
            "1) Create new backtest",
            "99) Exit program"
        ]
        choice: int = choose_option(title, options)

        # Check what the user chose to do
        if choice == 1:
            create_backtest()
            x = 0
        elif choice == 99:
            sys.exit()


def main():
    display_main_menu()


if __name__ == "__main__":
    main()
