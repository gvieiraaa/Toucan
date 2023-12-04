import asyncio
import datetime
import io

import httpx
import disnake
from disnake.ext import commands, tasks
from bs4 import BeautifulSoup
from dataclasses import dataclass, field

from config import LAB_CHANNEL, LAB_TRIALS_MESSAGE

@dataclass
class Lab:
    name: str
    url: str
    date: str
    img: bytes = field(repr=False)
    compass: str

    def equal_time(self, other_dt: datetime.datetime) -> bool:
        other_date = (
            other_dt.strftime(r"%B ") +
            other_dt.strftime(r"%d, ").lstrip('0') +
            other_dt.strftime(r"%Y")
        )
        return self.date == other_date


class Labs(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.lab_list = [f"{x} LAB" for x in ("NORMAL", "CRUEL", "MERC", "UBER")]
        self.last_full_lab = disnake.utils.utcnow() - datetime.timedelta(days=9)
        self.task_update_labs.start()

    async def get_labs(self) -> list[Lab]:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as c:
            r = await c.get("https://www.poelab.com/")
            soup = BeautifulSoup(r, "html5lib")
            labs = {lab: soup.find("a", string=lab)["href"] for lab in self.lab_list}
            assert len(labs) == 4
            print("labs from poelab:", labs, flush=True)
            updated_labs = []
            async with asyncio.TaskGroup() as tg:
                for lab in self.lab_list:
                    updated_labs.append(tg.create_task(self.get_lab(labs[lab], lab, c)))
            return [x.result() for x in updated_labs]

    async def get_lab(self, url: str, name: str, client: httpx.AsyncClient) -> Lab:
        result = await client.get(url)
        soup = BeautifulSoup(result, "html5lib")
        date: str = soup.find("span", class_="entry-meta-date updated").a.string
        img = await client.get(soup.find("img", id="notesImg")["src"])
        compass = soup.find("p", id="compassFile").a["href"]
        assert all([date, img, compass])
        return Lab(name, url, date, img.content, compass)

    @commands.slash_command(description="Updates the labs in the lab channel.")
    @commands.default_member_permissions(administrator=True)
    async def update_labs(self, inter: disnake.ApplicationCommandInteraction, forced: bool = False):
        await inter.response.defer(ephemeral=True)
        await self._update_labs(forced)
        await inter.edit_original_message("done!")

    @tasks.loop(time=[datetime.time(0, m) for m in range(0, 60, 10)] + [datetime.time(h, 0) for h in range(1, 24)])
    async def task_update_labs(self):
        try:
            await self._update_labs(False)
        except Exception as e:
            print("Error: ", e, flush=True)

    async def _update_labs(self, forced=False):
        now = disnake.utils.utcnow()
        if self.last_full_lab.date() == now.date() and not forced:
            return
        all_labs = await self.get_labs()
        if all_labs is None:
            return
        up_to_date_counter = sum(1 for lab in all_labs if lab.equal_time(now))

        if up_to_date_counter == 0 and not forced:
            return

        channel = self.bot.get_channel(LAB_CHANNEL)
        async for message in channel.history(limit=20):
            if message.id != LAB_TRIALS_MESSAGE:
                await message.delete()
            await asyncio.sleep(0.2)
        for lab in all_labs:
            embed = disnake.Embed(
                title=lab.name, description=f"Data: {lab.date}",
                url=lab.url
            )
            file = io.BytesIO(lab.img)
            file.seek(0)
            filename = lab.name.lower().replace(' ', '_')
            img = disnake.File(fp=file, filename=f"{filename}.jpg")
            embed.set_image(url=f"attachment://{filename}.jpg")
            await channel.send(embed=embed, file=img)

        next_midnight = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + datetime.timedelta(days=1)
        await channel.send(
            f"Próximo lab: {disnake.utils.format_dt(next_midnight, style='R')}\nSe a data acima já passou, as imagens ainda estão desatualizadas."
        )
        if up_to_date_counter < 4:
            singular = up_to_date_counter == 1
            await channel.send(
                f"Atenção: Apenas {up_to_date_counter} dos {len(self.lab_list)} labs {('foram','foi')[singular]} atualizado{('s','')[singular]} pelo poelab.com até agora."
            )
        else:
            self.last_full_lab = disnake.utils.utcnow()


def setup(bot):
    bot.add_cog(Labs(bot))
