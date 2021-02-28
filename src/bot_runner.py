import logging

from logging import Logger
from typing import Dict
from bot import Bot

logger: Logger = logging.getLogger("__main__")


class BotRunner:

    def __init__(self) -> None:
        self.bot_id = 0
        self.bots: Dict[int, Bot] = dict()

    def add_bot(self, bot: Bot) -> int:
        """
        Adds a trading bot to the bot runner.

        Parameters:
            bot: The bot that we want to add

        Returns:
            The id that got assigned to the bot
        """
        logger.info(f"Adding trading bot '{bot.name}' to bot runner...")
        new_id = self.bot_id + 1
        bot.id = new_id
        self.bots[bot.id] = bot
        self.bot_id = new_id
        return new_id

    def delete_bot(self, bot_id: int) -> None:
        logger.info(f"Removing bot '<name>' with ID {bot_id}...")
        self.bots.pop(bot_id)

    def start_bot(self, bot_id: int) -> None:
        logger.info(f"Starting bot '<name>' with ID {bot_id}...")
        bot: Bot = self.bots.get(bot_id)
        bot.status = Bot.STATUS_RUNNING

    def start_all_bots(self) -> None:
        logger.info(f"Starting all bots...")
        for bot in self.bots:
            bot.status = Bot.STATUS_RUNNING

    def stop_bot(self, bot_id: int) -> None:
        logger.info(f"Stopping bot '<name>' with ID {bot_id}...")
        bot: Bot = self.bots.get(bot_id)
        bot.status = Bot.STATUS_PAUSED

    def stop_all_bots(self) -> None:
        logger.info(f"Stopping all bots...")
        for bot in self.bots:
            bot.status = Bot.STATUS_PAUSED
