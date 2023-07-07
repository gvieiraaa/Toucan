from disnake.ext import commands
import disnake
import httpx
from functools import cache
from io import BytesIO
from playwright.async_api import async_playwright


class Wiki(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.queries = dict()
        self.pw = None
        self.browser = None

    @commands.slash_command(description="Procurar item na wiki")
    async def wiki(self, inter: disnake.ApplicationCommandInteraction, item: str):
        await inter.response.defer(with_message=f"Procurando \"{item}\" na wiki...")
        if self.browser is None:
            self.pw = await async_playwright().start()
            self.browser = await self.pw.chromium.launch()
        page = await self.browser.new_page()
        await page.goto(f"https://www.poewiki.net/wiki/{item}")
        if len(await page.content()) < 16000:
            await inter.edit_original_message(f"A página \"{item}\" não foi encontrada na wiki.")
            page.close()
            return
        try:
            element = await page.query_selector("span.item-box")
            ss = BytesIO(await element.screenshot(type="png", timeout=4000))
        except:
            element = None
            ss = None
        if element and ss:
            embed = disnake.Embed(title=item, url=page.url)
            img = disnake.File(fp=ss, filename=f"item.jpg")
            embed.set_image(url=f"attachment://item.jpg")
            await inter.edit_original_message(embed=embed, file=img)
        else:
            await inter.edit_original_message(page.url)
        await page.close()
        
    @wiki.autocomplete("item")
    async def wiki_autocomplete(self, inter: disnake.ApplicationCommandInteraction, item: str):
        return await self.cached_wiki_query(item.lower())
        
    async def cached_wiki_query(self, item: str):
        if item in self.queries:
            print(item, "is cached.", flush=True)
            return self.queries[item]
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://www.poewiki.net/api.php?action=query&list=allpages&apprefix={item}&aplimit=25&format=json")
        query_list = [item["title"] for item in r.json()["query"]["allpages"]]
        self.queries[item] = query_list
        return query_list

def setup(bot):
    bot.add_cog(Wiki(bot))
