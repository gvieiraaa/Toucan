from disnake.ext import commands

class Lab(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

def setup(bot):
    bot.add_cog(Lab(bot))