from disnake.ext import commands
import disnake
from config import INVITE, FACEBOOK


class Users(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(description="Link de convite para este discord.")
    async def invite(self, inter: disnake.ApplicationCommandInteraction):
        await inter.send(f"Link de convite para este discord:\n{INVITE}")

    @commands.slash_command(description="Informações sobre este servidor.")
    async def info(self, inter: disnake.ApplicationCommandInteraction):
        poe_counter = 0
        for member in inter.guild.members:
            if member.activity is not None and member.activity.name == "Path of Exile":
                poe_counter += 1
        await inter.send(
            f"Guild criada em: {inter.guild.created_at.strftime(r'%d/%m/%Y')}\n"
            f"Total de membros: {inter.guild.member_count}\n"
            f"{len(inter.guild.emojis)}/{inter.guild.emoji_limit} emojis usados\n"
            f"{poe_counter} estão jogando Path of Exile no momento"
        )
        
    @commands.slash_command(description="Link do facebook do Path of Exile Brasil.")
    async def facebook(self, inter: disnake.ApplicationCommandInteraction):
        await inter.send(f"Link do facebook do Path of Exile Brasil:\n<{FACEBOOK}>")


def setup(bot):
    bot.add_cog(Users(bot))
