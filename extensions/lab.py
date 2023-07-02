import httpx
import disnake
from disnake.ext import commands, tasks
import datetime
from bs4 import BeautifulSoup
import asyncio
from config import LAB_CHANNEL, LAB_TRIALS_MESSAGE


class Lab(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.task_update_labs.start()
        self.lab_list = ["UBER LAB", "MERC LAB", "CRUEL LAB", "NORMAL LAB"]
        self.last_full_lab = disnake.utils.utcnow() - datetime.timedelta(days=9)

    async def get_labs(self) -> dict:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as c:
            r = await c.get("https://www.poelab.com/")
            soup = BeautifulSoup(r, "html5lib")
            labs = {lab: soup.find("a", string=lab)["href"] for lab in self.lab_list}
            assert len(labs) == 4
            print("labs from poelab:", labs, flush=True)
            updated_labs = {}
            async with asyncio.TaskGroup() as tg:
                for lab in self.lab_list:
                    updated_labs[lab] = tg.create_task(self.get_lab(labs[lab], c))
            all_labs = {x: y.result() for x, y in updated_labs.items()}
            print("all labs:", all_labs)
            return all_labs

    async def get_lab(self, url: str, client: httpx.AsyncClient) -> tuple:
        result = await client.get(url)
        soup = BeautifulSoup(result, "html5lib")
        date = soup.find("span", class_="entry-meta-date updated").a.string
        img = soup.find("img", id="notesImg")["src"]
        json = soup.find("p", id="compassFile").a["href"]
        assert all(x is not None for x in [date, img, json])
        return (url, date, img, json)

    @commands.slash_command(description="Updates the labs in the lab channel.")
    @commands.default_member_permissions(administrator=True)
    async def update_labs(self, inter: disnake.ApplicationCommandInteraction, forced: bool = False):
        await inter.response.defer(ephemeral=True)
        await self._update_labs(forced)
        await inter.edit_original_message("done!")

    @tasks.loop(time=[datetime.time(h, m) for h in range(24) for m in range(0, 60, 10)])
    async def task_update_labs(self):
        await self._update_labs(False)

    async def _update_labs(self, forced=False):
        now = disnake.utils.utcnow()
        if self.last_full_lab.date() == now.date() and not forced:
            return
        try:
            all_labs = await self.get_labs()
        except:
            raise("Could not get labs")

        up_to_date_counter = len(
            [True for lab in self.lab_list if now.strftime(f"%B {now.strftime('%d').lstrip('0')}, %Y") == all_labs[lab][1]]
        )
        print(up_to_date_counter, flush=True)

        if up_to_date_counter == 0 and not forced:
            return

        channel = self.bot.get_channel(LAB_CHANNEL)
        async for message in channel.history(limit=20):
            if message.id != LAB_TRIALS_MESSAGE:
                await message.delete()
            await asyncio.sleep(0.2)
        for lab in reversed(self.lab_list):
            embed = disnake.Embed(
                title=lab, description=f"Data: {all_labs[lab][1]}", url=all_labs[lab][0]
            )
            embed.set_image(url=all_labs[lab][2])
            await channel.send(embed=embed)
            await asyncio.sleep(0.2)

        next_midnight = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + datetime.timedelta(days=1)
        await channel.send(
            f"Próximo lab: {disnake.utils.format_dt(next_midnight, style='R')}\nSe a data acima já passou, as imagens ainda estão desatualizadas."
        )
        if up_to_date_counter < 4:
            singular = up_to_date_counter == 1
            await channel.send(
                f"Atenção: Apenas {up_to_date_counter} dos {len(self.lab_list)} labs {'foi' if singular else 'foram'} atualizado{'' if singular else 's'} pelo poelab.com até agora."
            )
        else:
            self.last_full_lab = disnake.utils.utcnow()


def setup(bot):
    bot.add_cog(Lab(bot))
