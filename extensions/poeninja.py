from disnake.ext import commands
import disnake
import math
import tabulate
import httpx
from config import LEAGUE


class PoeNinja(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(description=f"Preço de divine/chaos na liga {LEAGUE}.")
    async def divine(self, inter: disnake.ApplicationCommandInteraction):
        await self.divine_chaos(inter)

    @commands.slash_command(description=f"Preço de divine/chaos na liga {LEAGUE}.")
    async def chaos(self, inter: disnake.ApplicationCommandInteraction):
        await self.divine_chaos(inter)

    async def divine_chaos(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://poe.ninja/api/data/currencyoverview?league=Crucible&type=Currency"
                )
                response = response.json()
        except:
            await inter.edit_original_message("Não foi possível verificar o preço de divine/chaos.")
            return
        divine_in_chaos = None
        for currency in response["lines"]:
            if currency["currencyTypeName"] == "Divine Orb":
                divine_in_chaos = currency["receive"]["value"]
                break
        if divine_in_chaos is None:
            await inter.edit_original_message(
                "Não foi possível verificar o preço de divine/chaos."
            )
            return
        msg = f"Segundo o poe.ninja uma divine vale **{math.floor(divine_in_chaos)} chaos** na liga {LEAGUE}."
        t1 = ["divines"].extend([f"{i/10}" for i in range(1, 10)])
        t2 = ["chaos"].extend([f"{math.ceil(i * (divine_in_chaos / 10))}" for i in range(1, 10)])
        tabulated = tabulate.tabulate(tabular_data=[t1, t2], numalign="center", tablefmt="plain")
        await inter.edit_original_message(f"{msg}\n\n`Particionado:\n{tabulated}`")


def setup(bot):
    bot.add_cog(PoeNinja(bot))
