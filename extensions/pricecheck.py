import base64
import asyncio
import io

from disnake.ext import commands, tasks
import disnake
import httpx

from config import PRICE_CHECK, LEAGUE


class PriceCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.instructions.start()

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.channel.id != PRICE_CHECK:
            return
        if message.author.bot:
            return
        if any(
            [
                len(message.content) < 50,
                message.content.count("--------") < 3,
                "Rarity: Rare" not in message.content,
            ]
        ):
            reply = await message.reply(
                "A API só aceita fazer price check de itens raros e em inglês"
            )
            await reply.delete(delay=8)
            await message.delete(delay=8)
            return
        await self.response_handler(message)

    async def response_handler(self, message: disnake.Message):
        item = base64.b64encode(bytes(message.content, "utf-8"))
        league = LEAGUE
        error = False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=f'https://www.poeprices.info/api?i={item.decode("utf-8")}&l={league}'
                )
        except:
            error = True
        response_json: dict = response.json()
        if response_json.get("error", None) != 0 or error:
            reply = await message.reply("Algo deu errado. O item pode não ser válido.")
            await reply.delete(delay=8)
            await message.delete(delay=8)
            return

        fp = io.BytesIO(bytes(message.content.encode("utf-8")))
        file = disnake.File(fp, "item.txt")
        embed = await self.create_embed(message, response_json)

        await message.channel.send(message.author.mention, file=file, embed=embed)
        await message.delete()

    async def create_embed(
        self, message: disnake.Message, prediction: dict
    ) -> disnake.Embed:
        score_color = {
            "baixa": disnake.Colour.red(),
            "média": disnake.Colour.yellow(),
            "alta": disnake.Colour.green(),
        }
        score = prediction.get("pred_confidence_score", 0)
        confidence = ""
        if score < 55:
            confidence = "baixa"
        elif 55 <= score < 80:
            confidence = "média"
        else:
            confidence = "alta"

        embed = disnake.Embed(
            title=f'Entre {prediction["min"]:.2f} e {prediction["max"]:.2f} {prediction["currency"]}',
            description=f"Confiança de {score:.2f}% ({confidence})",
            colour=score_color[confidence],
        )
        embed.set_author(
            name=message.author.display_name, icon_url=message.author.avatar.url
        )

        if "pred_explanation" not in prediction:
            return embed

        embed.add_field(
            name="Participação dos mods na estimativa:", value="", inline=False
        )

        for mod, weight in prediction["pred_explanation"]:
            embed.add_field(name=mod, value=f"{weight:.2%}")

        return embed

    @tasks.loop(minutes=5)
    async def instructions(self):
        instruction = "Para fazer price check, copie o item no jogo com `ctrl+c` e cole aqui com `ctrl+v`.\n"
        instruction += f"A API usada só aceita itens raros e em inglês (www.poeprices.info). Liga {LEAGUE}.\n"
        instruction += "### **IMPORTANTE**: Não confie cegamente no resultado.\n"
        instruction += (
            "É uma **estimativa** baseada em A.I., e pode estar bem longe da realidade."
        )
        await asyncio.sleep(10)
        channel = self.bot.get_channel(PRICE_CHECK)
        async for message in channel.history(limit=1):
            if instruction in message.content:
                return
        async for message in channel.history(limit=20):
            if instruction in message.content:
                await message.delete()
        await channel.send(instruction)


def setup(bot):
    bot.add_cog(PriceCheck(bot))
