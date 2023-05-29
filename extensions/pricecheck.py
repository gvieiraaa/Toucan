"""https://www.poeprices.info/api?i=&l=Crucible"""

"""{"min": 69.84, "max": 104.75999999999999, "currency": "chaos", "warning_msg": "Low confidence score (54.9%), prediciton might not be reliable. Providing feedback can let the prediction engine become smarter.", "error": 0, "pred_explanation": [["Has # Abyssal Socket", 0.41949645619904424], ["(pseudo) (total) #% increased Cold Damage with Attack Skills", 0.1933236111240013], ["(pseudo) +#% total Elemental Resistance", 0.11132040750139649], ["(pseudo) (total) #% increased Fire Damage with Attack Skills", 0.02763621536170043], ["(pseudo) (total) #% increased Lightning Damage with Attack Skills", 0.00709136020307048], ["(pseudo) (total) +#% to Fire Resistance", 0.002874107010139724], ["(pseudo) (total) +#% to Lightning Resistance", 0.0024207715732346407], ["(pseudo) (total) +# to maximum Life", -0.23583707102741272]], "pred_confidence_score": 54.88007246525313, "error_msg": ""}"""

from disnake.ext import commands, tasks
import disnake
import httpx
import base64
import asyncio
from config import POE, BOT


class PriceCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.instructions.start()
        
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.channel.id != BOT['PRICE_CHECK']:
            return
        if message.author.bot:
            return
        if any([
            len(message.content) < 50,
            message.content.count('--------') < 3,
            'Rarity: Rare' not in message.content,
        ]):
            reply = await message.reply('A API só aceita fazer price check de itens raros e em inglês')
            await reply.delete(delay=8)
            await message.delete(delay=8)
            return
        await self.price_it(message)
    
    async def price_it(self, message: disnake.Message):
        item = base64.b64encode(bytes(message.content, 'utf-8'))
        league = POE['LEAGUE']
        async with httpx.AsyncClient() as client:
            response = await client.get(url=f'https://www.poeprices.info/api?i={item.decode("utf-8")}&l={league}')
        await message.reply(response.json())

    @tasks.loop(minutes=5)
    async def instructions(self):
        instruction =  'Para fazer price check, copie o item no jogo com `ctrl+c` e cole aqui com `ctrl+v`.\n'
        instruction += f'A API usada só aceita itens raros e em inglês (www.poeprices.info). Liga {POE["LEAGUE"]}.\n'
        instruction += '### **IMPORTANTE**: Não confie cegamente no resultado.\n'
        instruction += 'É uma **estimativa** baseada em A.I., e pode estar bem longe da realidade.'
        await asyncio.sleep(10)
        channel = self.bot.get_channel(BOT['PRICE_CHECK'])
        async for message in channel.history(limit=1):
            if instruction in message.content:
                return
        async for message in channel.history(limit=20):
            if instruction in message.content:
                await message.delete()
        await channel.send(instruction)


def setup(bot):
    bot.add_cog(PriceCheck(bot))