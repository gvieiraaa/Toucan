from disnake.ext import commands
import disnake
from config import BOT

class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(description="Reloads an extension.")
    @commands.is_owner()
    async def reload_extension(
        self,
        inter: disnake.ApplicationCommandInteraction,
        extension: str = commands.Param(choices=BOT["EXTENSIONS"]),
    ):
        try:
            self.bot.reload_extension(f"extensions.{extension}")
        except Exception as e:
            await inter.send(f"Could not reload the {extension} extension. Error:\n{e}", ephemeral=True)
            return
        await inter.send(f"The `{extension}` extension was reloaded.", ephemeral=True)

    @commands.slash_command(description="Testing something")
    @commands.is_owner()
    async def t(self, inter: disnake.ApplicationCommandInteraction):
        import datetime
        await inter.send(datetime.datetime.utcnow())


def setup(bot):
    bot.add_cog(Owner(bot))
