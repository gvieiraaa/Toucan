import asyncio
import datetime
import json
import logging
import os

import disnake
from disnake.ext import commands, tasks

from database import Database
from gpt import get_gpt, respond
from auth import SECRETS

DEBUG = False
command_sync_flags = commands.CommandSyncFlags(
    allow_command_deletion=False,
    sync_commands=False,
    sync_commands_debug=False,
    sync_global_commands=False,
    sync_guild_commands=False,
    sync_on_cog_actions=False,
)

intents = disnake.Intents.all()
if DEBUG:
    bot = commands.InteractionBot(intents=intents, command_sync_flags=command_sync_flags)
else:
    bot = commands.InteractionBot(intents=intents)

db = Database(f'{os.path.dirname(__file__)}/db/db.db')

def setup_logger():
    # init first log file
    if not os.path.isfile("logs/log.log"):
        # we have to make the logs dir before we log to it
        if not os.path.exists("logs"):
            os.makedirs("logs")
        open("logs/log.log", "w+")

    # set logging levels for various libs
    logging.getLogger("disnake").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.INFO)

    # we want out logging formatted like this everywhere
    fmt = logging.Formatter(
        "{asctime} [{levelname}] {name}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

    file: logging.Handler. = logging.handlers.TimedRotatingFileHandler(
        "logs/log.log", when="midnight", encoding="utf-8-sig"
    )
    file.setFormatter(fmt)
    file.setLevel(logging.INFO)

    # get the __main__ logger and add handlers
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)
    root.addHandler(file)

    return logging.getLogger(__name__)

if __name__ == '__main__':
    log = setup_logger()
    bot.add_cog(Thread_updates(bot))
    bot.run(SECRETS["BOT_TOKEN"])