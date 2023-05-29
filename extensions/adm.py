from disnake.ext import commands
import disnake


class Adm(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def purge(
        self, inter: disnake.ApplicationCommandInteraction, amount: int = 100
    ):
        channel = self.bot.get_channel(inter.channel_id)
        async for message in channel.history(limit=amount):
            await message.delete()
        inter.send(f"Purged", ephemeral=True)


def setup(bot):
    bot.add_cog(Adm(bot))
