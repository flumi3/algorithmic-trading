from bot_runner import BotRunner
from cli.cli import CommandLineInterface


def main():
    # If db exists
    #   load config
    # else
    #   create new bot runner
    bot_runner: BotRunner = BotRunner()
    cli: CommandLineInterface = CommandLineInterface(bot_runner)
    cli.display_main_menu()


if __name__ == "__main__":
    main()
