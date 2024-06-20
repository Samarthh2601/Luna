import discord
from discord.ext import commands
from discord import app_commands, Interaction
from io import BytesIO

from ..core import Luna

class Server(commands.GroupCog, name="server"):
    def __init__(self, bot: Luna):
        self.bot = bot


    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.command(name="edit", description="Edit a server")
    async def edit(self, inter: Interaction, name: str=None, region: str=None) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        await inter.guild.edit(name=name or inter.guild.name, region=region or inter.guild.region)
        embed = discord.Embed(title="Server Edited", description=f"Server {inter.guild.name} has been edited", color=discord.Color.blurple()).add_field(name="ID", value=inter.guild.id).add_field(name="Owner", value=inter.guild.owner).add_field(name="Region", value=inter.guild.region).add_field(name="Members", value=inter.guild.member_count).add_field(name="Created At", value=inter.guild.created_at)
        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="info", description="Get information about a server")
    async def info(self, inter: Interaction) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        embed = discord.Embed(title="Server Information", description=f"Server {inter.guild.name}", color=discord.Color.blurple()).add_field(name="ID", value=inter.guild.id).add_field(name="Owner", value=inter.guild.owner).add_field(name="Region", value=inter.guild.region).add_field(name="Members", value=inter.guild.member_count).add_field(name="Created At", value=inter.guild.created_at)
        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="emoji", description="Add an emoji to the server")
    async def emoji(self, inter: discord.Interaction, emoji_name: str, image_url: str) -> discord.InteractionMessage | None:
        await inter.response.defer(ephemeral=True, thinking=True)

        async with self.bot.http_client as session:
            async with session.get(image_url) as response:
                if response.status in range(200, 299):
                    try:
                        img_or_gif = BytesIO(await response.read())
                        b_value = img_or_gif.getvalue()
                        emoji = await inter.guild.create_custom_emoji(image=b_value, name=emoji_name)
                    except discord.HTTPException:
                        await inter.edit_original_response(content="File size is too big!")
                        return await session.close()
                        
                    embed = discord.Embed(title="Created an emoji!", description=f"Created By: {inter.user.mention}").set_thumbnail(url=inter.user.display_avatar.url)
                    if emoji.animated is True: embed.add_field(name=f"Emoji name: {emoji.name}", value=f"<a:{emoji.name}:{emoji.id}>")
                    else: embed.add_field(name=f"Emoji name: {emoji.name}", value=f"<:{emoji.name}:{emoji.id}>")
                    
                    await inter.edit_original_response(embed=embed)
                else:
                    await inter.edit_original_response(content="Could not get that emoji!")
                await session.close()

    @app_commands.command(name="rename_emoji", description="Edit an emoji")
    async def rename_emoji(self, inter: Interaction, emoji: discord.Emoji, name: str) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        await emoji.edit(name=name)
        embed = discord.Embed(title="Emoji Edited", description=f"Emoji {emoji.name} has been edited", color=discord.Color.blurple()).add_field(name="ID", value=emoji.id).add_field(name="Name", value=emoji.name)
        await inter.edit_original_response(embed=embed)
                
async def setup(bot: Luna):
    await bot.add_cog(Server(bot))