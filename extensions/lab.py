import httpx
import disnake
from disnake.ext import commands, tasks
import datetime
import time
from bs4 import BeautifulSoup
import asyncio
from config import BOT


class Lab(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.task_update_labs.start()

    async def get_labs(self) -> dict:
        lab_list = ["UBER LAB", "MERC LAB", "CRUEL LAB", "NORMAL LAB"]
        async with httpx.AsyncClient(follow_redirects=True) as c:
            r = await c.get("https://www.poelab.com/")
            soup = BeautifulSoup(r, "html5lib")
            labs = {lab: soup.find("a", string=lab)["href"] for lab in lab_list}
            assert len(labs) == 4
            print(labs)
            updated_labs = {}
            async with asyncio.TaskGroup() as tg:
                for lab in lab_list:
                    updated_labs[lab] = tg.create_task(self.get_lab(labs[lab], c))
            all_labs = {x: y.result() for x, y in updated_labs.items()}
            print(all_labs)
            return all_labs

    async def get_lab(self, url: str, c: httpx.AsyncClient) -> tuple:
        result = await c.get(url)
        soup = BeautifulSoup(result, "html5lib")
        date = soup.find("span", class_="entry-meta-date updated").a.string
        img = soup.find("img", id="notesImg")["src"]
        json = soup.find("p", id="compassFile").a["href"]
        assert all(x is not None for x in [date, img, json])
        return (url, date, img, json)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def update_labs(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        await self._update_labs()
        await inter.edit_original_message("done!")

    @tasks.loop(time=[datetime.time(n, 30) for n in range(4)])
    async def task_update_labs(self):
        await self._update_labs()

    async def _update_labs(self):
        channel = self.bot.get_channel(BOT["LAB_CHANNEL"])
        async for message in channel.history(limit=10):
            await message.delete()
            await asyncio.sleep(0.2)
        all_labs = await self.get_labs()
        for lab in reversed(["UBER LAB", "MERC LAB", "CRUEL LAB", "NORMAL LAB"]):
            embed = disnake.Embed(
                title=lab, description=f"Data: {all_labs[lab][1]}", url=all_labs[lab][0]
            )
            embed.set_image(url=all_labs[lab][2])
            await channel.send(embed=embed)
            await asyncio.sleep(0.2)
        now = datetime.datetime.utcnow()
        next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now > next_midnight:
            next_midnight += datetime.timedelta(days=1)
        next_midnight -= datetime.timedelta(hours=3)
        unix_time = int(time.mktime(next_midnight.timetuple()))
        await channel.send(
            f"Próximo lab: <t:{unix_time}:R>\nSe a data acima já passou, as imagens ainda estão desatualizadas."
        )


def setup(bot):
    bot.add_cog(Lab(bot))
