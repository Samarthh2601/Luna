import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
import os
from ..core import Luna
from ..secrets import Info

def get_all_extension_choices() -> list:
    return [app_commands.Choice(name=file[:-3].capitalize(), value=f"{Info.FORMATTED_EXTENSIONS_PATH}{file[:-3]}") for file in os.listdir(Info.AUTO_LOAD_EXTENSIONS_FROM) if file.endswith(".py") and not file.startswith("_")]

class Admin(commands.GroupCog, name="admin"):
    def __init__(self, bot: Luna):
        self.bot = bot

    @app_commands.choices(extension=get_all_extension_choices())
    @app_commands.command(name="reload_extension", description="Reloads all extensions")
    async def reload_extensions(self, inter: Interaction, extension: str = None):
        await inter.response.defer(ephemeral=True, thinking=True)
        if extension is None:
            await self.bot.auto_reload_extensions()
            content="All Extensions have been reloaded!"
        else:
            await self.bot.reload_extension(extension)
            content = f"Reloaded `{extension}`!"
        await inter.edit_original_response(content=content)
    
    @app_commands.command(name='all_guilds', description="Lists all guilds the bot is in")
    async def all_guilds(self, inter: Interaction):
        await inter.response.defer(ephemeral=True, thinking=True)
        embed = discord.Embed(title="All Guilds", description=len(self.bot.guilds), color=discord.Colour.random())
        await inter.edit_original_response(embed=embed)


async def setup(bot: Luna):
    await bot.add_cog(Admin(bot))