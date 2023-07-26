from disnake.ext import commands
import disnake

from config import LOG_CHANNEL, EXTENSIONS
from util.misc import get_unix_now


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_connect(self):
        pass

    async def on_resumed(self):
        await self.change_presence()
        await self.change_presence(
            activity=disnake.Game(name="Path of Exile", platform="PC"),
            status=disnake.Status.online,
        )

    async def on_ready(self):
        channel = self.get_channel(LOG_CHANNEL)
        await channel.send(f"Bot started {get_unix_now()}")
        await self.change_presence(
            activity=disnake.Game(name="Path of Exile", platform="PC"),
            status=disnake.Status.online,
        )
        print("ready", flush=True)

    async def on_message(self, message):
        await self.process_commands(message)

    def load_extensions(self):
        for name in EXTENSIONS:
            file_name = f"extensions.{name}"
            self.load_extension(file_name)

    async def on_message_delete(self, message: disnake.Message):
        if message.author.bot or message.author.id == self.owner_id:
            return
        adm_channel = self.get_channel(LOG_CHANNEL)
        await adm_channel.send(
            f"User {message.author.mention} deleted a message in {message.channel.mention} ({disnake.utils.format_dt(disnake.utils.utcnow(), style='R')})\n"
            f"Message:\n{message.content}"
        )

    async def login(self, token: str) -> None:
        print("logging in", flush=True)
        self.load_extensions()
        return await super().login(token)

    async def on_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, error: commands.CommandError
    ):
        if isinstance(error, commands.CommandOnCooldown):
            await inter.send("Comando em cooldown.", ephemeral=True)
