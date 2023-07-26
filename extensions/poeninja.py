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
    @commands.cooldown(rate=1, per=240, type=commands.BucketType.guild)
    async def divine(self, inter: disnake.ApplicationCommandInteraction):
        await self.divine_chaos(inter)

    @commands.slash_command(description=f"Preço de divine/chaos na liga {LEAGUE}.")
    @commands.cooldown(rate=1, per=240, type=commands.BucketType.guild)
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
        except Exception as e:
            print(e, flush=True)
            await inter.edit_original_message(
                "Não foi possível verificar o preço de divine/chaos."
            )
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
        embed = disnake.Embed(
            title=f"{math.floor(divine_in_chaos)} chaos = 1 divine",
            url="https://poe.ninja/economy/challenge/currency/divine-orb",
        )
        t1 = ["divines"]
        t1.extend([f"{i/10}" for i in range(1, 10)])
        t2 = ["chaos"]
        t2.extend([f"{math.ceil(i * (divine_in_chaos / 10))}" for i in range(1, 10)])
        tabulated = tabulate.tabulate(
            tabular_data=[t1, t2], numalign="center", tablefmt="plain"
        )
        tabulated_code = "`" + tabulated.replace("\n", "`\n`") + "`"
        embed.add_field(name="Particionado:", value=tabulated_code, inline=True)
        embed.set_footer(
            text="poe.ninja - liga Crucible",
            icon_url="https://poe.ninja/images/ninja-logo.png",
        )
        await inter.edit_original_message(embed=embed)


def setup(bot):
    bot.add_cog(PoeNinja(bot))
