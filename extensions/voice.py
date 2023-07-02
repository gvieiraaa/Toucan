from disnake.ext import commands
import disnake
from config import LOG_CHANNEL, AFK_CHANNEL, GENERAL_CHANNEL, GUILD, ID
import asyncio

VOTE_THRESHOLD = 0.7


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.vote_emojis = ("✅", "❌")
        self.votes = dict()
        self.vote_in_place = False

    @commands.slash_command(
        description=f"Inicia uma votação para mover alguém para a sala de AFK."
    )
    async def vote_move(
        self, inter: disnake.ApplicationCommandInteraction, member: str
    ):
        member: int = int(member)
        try:
            members = [
                voice_member.id
                for voice_member in inter.author.voice.channel.members
            ]
        except AttributeError:
            await inter.send("Usuário não encontrado", ephemeral=True)
            return
        if member not in members:
            await inter.send("Usuário não encontrado", ephemeral=True)
            return
        if self.vote_in_place:
            await inter.send(
                "Uma votação já está acontecendo, aguarde até ela acabar.",
                ephemeral=True,
            )
            return
        member_obj = self.bot.get_user(member)
        await inter.send(
            f"Votação para mover o usuário {member_obj.display_name} para a sala {self.bot.get_channel(AFK_CHANNEL).mention} iniciada.",
            ephemeral=True,
        )
        log_channel = self.bot.get_channel(LOG_CHANNEL)
        self.vote_in_place = True
        target_member = self.bot.get_user(member)
        await log_channel.send(
            f"O usuário {inter.author.mention} iniciou uma votação para mover {target_member.mention}. Iniciada para o canal {inter.author.voice.channel.mention}."
        )
        await self._start_vote(member, inter.author.voice.channel.id)

    @vote_move.autocomplete("member")
    async def vote_move_autocomplete(
        inter: disnake.ApplicationCommandInteraction, string: str
    ):
        try:
            members = inter.author.voice.channel.members
        except AttributeError:
            return
        members_list = [member.display_name for member in members]
        if len(members_list) == len(set(members_list)):
            return {member.display_name:str(member.id) for member in members}
        else:
            return {f"{member.display_name}-{member.id}":str(member.id) for member in members}
        #return [f"{member.display_name}-{member.id}" for member in members]

    async def _start_vote(self, member: int, channel: int):
        general_channel = self.bot.get_channel(GENERAL_CHANNEL)
        target_member = self.bot.get_user(member)
        message = await general_channel.send(
            f"Votação para mover o usuário {target_member.display_name} "
            + f"para a sala {self.bot.get_channel(AFK_CHANNEL).mention} iniciada."
            + f"\nReaja com:\n{self.vote_emojis[0]} para mover\n{self.vote_emojis[1]} para não mover"
        )
        self.votes[message.id] = {
            "target": member,
            "channel": channel,
            "yes": set(),
            "no": set(),
            "message": message.id,
        }
        for emoji in self.vote_emojis:
            await message.add_reaction(emoji)
        await asyncio.sleep(120)
        try:
            await message.delete()
        except:
            pass
        self.vote_in_place = False

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: disnake.RawReactionActionEvent):
        await self.reaction_handler(reaction, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction: disnake.RawReactionActionEvent):
        await self.reaction_handler(reaction, "remove")

    async def reaction_handler(
        self, reaction: disnake.RawReactionActionEvent, reaction_type: str
    ):
        if reaction.message_id not in self.votes.keys():
            return
        if reaction.emoji.name not in self.vote_emojis:
            return
        if reaction.user_id == ID:
            return
        if reaction.user_id == self.votes[reaction.message_id]["target"]:
            return
        vote_type = "yes" if reaction.emoji.name == self.vote_emojis[0] else "no"
        if reaction_type == "add":
            self.votes[reaction.message_id][vote_type].add(reaction.user_id)
        else:
            self.votes[reaction.message_id][vote_type].remove(reaction.user_id)

        vote = self.votes[reaction.message_id]
        yes_set: set = vote["yes"]
        no_set: set = vote["no"]
        only_yes_set = yes_set - no_set
        channel_id = vote["channel"]
        channel = self.bot.get_channel(channel_id)
        voice_members = set(member.id for member in channel.members)
        if len(only_yes_set & voice_members) / len(voice_members) >= VOTE_THRESHOLD:
            message = self.bot.get_message(vote["message"])
            await message.delete()
            general_channel = self.bot.get_channel(GENERAL_CHANNEL)
            guild = self.bot.get_guild(GUILD)
            member = guild.get_member(vote["target"])
            afk_voice = guild.get_channel(AFK_CHANNEL)
            await member.move_to(afk_voice, reason="Votação (afk)")
            await general_channel.send("Usuário movido.")
            log_channel = self.bot.get_channel(LOG_CHANNEL)
            await log_channel.send(
                f"O usuário {member.mention} foi movido para a sala afk."
            )
            self.vote_in_place = False


def setup(bot):
    bot.add_cog(Voice(bot))
