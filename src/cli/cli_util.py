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


def choose_option(title: str, options: List[str]) -> int:
    text: FormattedText = FormattedText([("class:bold", title)])
    print_formatted_text(text, style=style)

    for option in options:
        print(option)
    print("")

    number: int = int(prompt("Enter number: ", validator=NumberValidator()))
    return number


# def radiolist_dialog(title='', values=None, style=None, async_=False):
#     # Add exit key binding.
#     bindings = KeyBindings()
#
#     @bindings.add('c-d')
#     def exit_(event):
#         """
#         Pressing Ctrl-d will exit the user interface.
#         """
#         event.app.exit()
#
#     @bindings.add("escape")
#     def exit_with_value(event):
#         """
#         Pressing Ctrl-a will exit the user interface returning the selected value.
#         """
#         event.app.exit(result=radio_list.current_value)
#
#     radio_list = RadioList(values)
#     application = Application(
#         layout=Layout(HSplit([Label(title), radio_list])),
#         key_bindings=merge_key_bindings(
#             [load_key_bindings(), bindings]),
#         mouse_support=True,
#         style=style,
#         full_screen=False)
#
#     if async_:
#         return application.run_async()
#     else:
#         return application.run()
