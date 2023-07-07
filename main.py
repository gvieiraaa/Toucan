import logging
import os
import disnake

from config import TOKEN, OWNER_ID, GUILD
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
    intents = disnake.Intents.default()
    intents.message_content = True
    intents.members = True
    command_prefix="."
    owner_id=OWNER_ID
    test_guilds=[GUILD]
    kwargs = {
        "command_prefix": command_prefix,
        "owner_id": owner_id,
        "test_guilds": test_guilds,
        "intents": intents,
    }
    bot = Bot(**kwargs)
    return bot


if __name__ == "__main__":
    log = setup_logger()
    bot = setup_bot()
    bot.run(TOKEN)
