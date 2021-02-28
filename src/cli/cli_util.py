import os

from typing import List
from prompt_toolkit import print_formatted_text, prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from cli.validators import NumberValidator

style: Style = Style.from_dict(
    {
        # Colored text
        "green": "ansibrightgreen",
        "cyan": "ansibrightcyan",
        "red": "ansired",
        "yellow": "ansiyellow",
        "blue": "ansiblue",
        "magenta": "ansibrightmagenta",

        # Special formatting
        "bold": "bold",
        "blink": "blink",
        "underline": "underline",
        "header": "ansibrightgreen bold",
    }
)


def clear_output():
    if os.name == "nt":
        os.system("cls")  # Windows
    else:
        os.system("clear")  # Unix


def display_header(header: str) -> None:
    clear_output()
    text: FormattedText = FormattedText([("class:header", header)])
    print_formatted_text(text, style=style)
    print("")


def print_bold(string: str) -> None:
    text: FormattedText = FormattedText([("class:bold", string)])
    print_formatted_text(text, style=style)


def choose_option(title: str, options: List[str], header: str, note: str = None) -> int:
    user_input: str = ""
    while user_input == "":
        display_header(header)
        text: FormattedText = FormattedText([("class:bold", title)])
        print_formatted_text(text, style=style)

        # Display all options
        for option in options:
            print(option)
        print("")
        if note:
            text: FormattedText = FormattedText([("class:yellow", "Note: " + note)])
            print_formatted_text(text, style=style)
            print("")

        # Get user input
        user_input = prompt("Enter number: ", validator=NumberValidator())
    return int(user_input)
