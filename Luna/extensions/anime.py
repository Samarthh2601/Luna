import pykawaii
import discord
from discord.ext import commands
from discord import app_commands, Interaction

from ..core import Luna

pykawaii_params =  ['waifu', 'neko', 'bully', 'cuddle', 'cry', 'hug', 'awoo', 'kiss', 'lick', 'pat', 'wave', 'bonk', 'blush', 'smile', 'highfive', 'handhold', 'bite', 'glomp', 'slap', 'kill', 'wink', 'kick', 'poke', 'happy', 'dance', 'cringe']

class Anime(commands.GroupCog, name="anime"):
    def __init__(self, bot: Luna) -> None:
        self.bot = bot
        self.client = pykawaii.Client().sfw

    @app_commands.choices(choice=([app_commands.Choice(name=param.capitalize(), value=param) for param in pykawaii_params])[:25])
    @app_commands.command(name="reaction", description="Get a reaction image from the bot!")
    async def reaction(self, inter: Interaction, member: discord.User | discord.Member, choice: str) -> None:
        await inter.response.defer(thinking=True)
        embed = discord.Embed(title=f"{choice.capitalize()}!", description=f"{inter.user.mention} and {member.mention}").set_image(url=await (getattr(self.client, choice))())
        await inter.edit_original_response(embed=embed)

async def setup(bot: Luna):
    await bot.add_cog(Anime(bot))