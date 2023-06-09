from disnake.ext import commands
import disnake


class Adm(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(description="Deletes messages in the current channel.")
    @commands.has_permissions(administrator=True)
    async def purge(
        self, inter: disnake.ApplicationCommandInteraction, amount: int = 100
    ):
        await inter.response.defer(ephemeral=True)
        channel = self.bot.get_channel(inter.channel_id)
        counter = 0
        async for message in channel.history(limit=amount):
            await message.delete()
            counter += 1
        await inter.edit_original_message(f"Purged {counter} messages.")
        
    @commands.slash_command(description="Pings the server")
    @commands.has_permissions(administrator=True)
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        await inter.send(f"Pong! ({int(self.bot.latency * 1000)} ms)")



def setup(bot):
    bot.add_cog(Adm(bot))
