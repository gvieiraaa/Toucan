import logging
import os

from config import BOT
from bot import Bot


def setup_logger():
    logger = logging.getLogger("disnake")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
        filename=f"{os.path.dirname(__file__)}/logs/disnake.log",
        encoding="utf-8",
        mode="w",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)
    return logger


def setup_bot():
    bot = Bot()
    return bot


if __name__ == "__main__":
    log = setup_logger()
    bot = setup_bot()
    bot.run(BOT["TOKEN"])
