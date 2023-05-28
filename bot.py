import os
from disnake.ext import commands
import disnake
from config import BOT

class Bot(commands.InteractionBot):
    def __init__(self, **kwargs):
        super().__init__(
            owner_id=BOT['OWNER_ID'],
            test_guilds=[BOT['GUILD']],
            intents=disnake.Intents.all(),
            **kwargs
        )

    async def on_connect(self):
        pass

    async def on_resumed(self):
        pass

    async def on_ready(self):
        print('ready', flush=True)

    async def on_message(self, message):
        print(message, flush=True)

    def load_extensions(self):
        for name in BOT['EXTENSIONS']:
            file_name = f'extensions.{name}'
            self.load_extension(file_name)

    async def login(self, token: str) -> None:
        print('logging in', flush=True)
        self.load_extensions()
        return await super().login(token)