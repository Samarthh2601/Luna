import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from ..core import Luna


class General(commands.GroupCog, name="general"):
    def __init__(self, bot: Luna):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, inter: Interaction) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        embed = discord.Embed(title="My Latency", description=f"{round(self.bot.latency*1000)}ms", colour=discord.Colour.random())
        await inter.edit_original_response(embed=embed)
    
    @app_commands.command(name="uptime", description="Check the bot's uptime")
    async def uptime(self, inter: Interaction) -> None:
        await inter.response.defer(ephemeral=True, thinking=True) 
        embed = discord.Embed(title="My Uptime", description=f"Days:`{self.bot.uptime.days}` \nHours: `{self.bot.uptime.hours}` \nMinutes: `{self.bot.uptime.minutes}` \nSeconds: `{self.bot.uptime.seconds}`", color=discord.Color.random())
        await inter.edit_original_response(embed=embed)

async def setup(bot: Luna) -> None:
    await bot.add_cog(General(bot))