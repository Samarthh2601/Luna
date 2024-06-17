import discord
from discord.ext import commands
from discord import app_commands, Interaction

from ..core import Luna

class Roles(commands.GroupCog, name="role"):
    def __init__(self, bot: Luna):
        self.bot = bot

    async def cog_check(self, inter: Interaction) -> bool: return bool(inter.guild and inter.user.guild_permissions.manage_roles and inter.guild.me.guild_permissions.manage_roles or inter.user.id == inter.guild.owner_id)


    @app_commands.choices(mentionable=[app_commands.Choice(name="Yes", value=1), app_commands.Choice(name="No", value=0)])
    @app_commands.command(name="create", description="Create a role")
    async def create(self, inter: Interaction, name: str, color_hexcode: str, mentionable: int) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        mentionable = bool(mentionable)
        role = await inter.guild.create_role(name=name, color=discord.Color.from_str(color_hexcode), mentionable=mentionable)
        embed = discord.Embed(title="Role Created", description=f"Role {role.mention} has been created", color=role.color).add_field(name="Mentionable", value=mentionable).add_field(name="Color", value=role.color).add_field(name="Position", value=role.position).add_field(name="ID", value=role.id).add_field(name="Created At", value=role.created_at).add_field(name="Hoisted", value=role.hoist).add_field(name="Managed", value=role.managed)
        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="delete", description="Delete a role")
    async def delete(self, inter: Interaction, role: discord.Role) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        await role.delete()
        await inter.edit_original_response(content=f"Role `{role}` has been deleted")

    @app_commands.choices(mentionable=[app_commands.Choice(name="Yes", value=1), app_commands.Choice(name="No", value=0)])
    @app_commands.command(name="edit", description="Edit a role")
    async def edit(self, inter: Interaction, role: discord.Role, name: str=None, color_hexcode: str=None, mentionable: int=None) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        mentionable = bool(mentionable)
        await role.edit(name=name or role.name, color=discord.Color.from_str(color_hexcode) or role.color, mentionable=mentionable or role.mentionable)
        embed = discord.Embed(title="Role Edited", description=f"Role {role.mention} has been edited", color=role.color).add_field(name="Mentionable", value=mentionable).add_field(name="Color", value=role.color).add_field(name="Position", value=role.position).add_field(name="ID", value=role.id).add_field(name="Created At", value=role.created_at).add_field(name="Hoisted", value=role.hoist).add_field(name="Managed", value=role.managed)
        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="list", description="List all roles")
    async def list(self, inter: Interaction) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        roles = inter.guild.roles
        embed = discord.Embed(title="Roles", description="\n".join([role.mention for role in roles]), color=discord.Color.blurple())
        await inter.edit_original_response(embed=embed)
    
    @app_commands.command(name="info", description="Get information about a role")
    async def info(self, inter: Interaction, role: discord.Role) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        embed = discord.Embed(title="Role Information", description=f"Role {role.mention}", color=role.color).add_field(name="Mentionable", value=role.mentionable).add_field(name="Color", value=role.color).add_field(name="Position", value=role.position).add_field(name="ID", value=role.id).add_field(name="Created At", value=role.created_at).add_field(name="Hoisted", value=role.hoist).add_field(name="Managed", value=role.managed).add_field(name="Members", value=len(role.members))
        await inter.edit_original_response(embed=embed)
    
    @app_commands.command(name="add", description="Add a role to a member")
    async def add(self, inter: Interaction, member: discord.Member, role: discord.Role) -> discord.InteractionResponse | None:
        await inter.response.defer(ephemeral=True, thinking=True)
        if role in member.roles:
            return await inter.edit_original_response(content=f"{member.mention} already has {role.mention}")
        await member.add_roles(role)
        await inter.edit_original_response(content=f"{role.mention} has been added to {member.mention}")

    @app_commands.command(name="remove", description="Remove a role from a member")
    async def remove(self, inter: Interaction, member: discord.Member, role: discord.Role) -> discord.InteractionMessage | None:
        await inter.response.defer(ephemeral=True, thinking=True)
        if role not in member.roles:
            return await inter.edit_original_response(content=f"{member.mention} does not have {role.mention}")
        await member.remove_roles(role)
        await inter.edit_original_response(content=f"{role.mention} has been removed from {member.mention}")
    
    @app_commands.command(name="list_members", description="List all members with a role")
    async def list_members(self, inter: Interaction, role: discord.Role) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        embed = discord.Embed(title="Members", description="\n".join([member.mention for member in role.members]), color=discord.Color.blurple())
        await inter.edit_original_response(embed=embed)

async def setup(bot: Luna) -> None:
    await bot.add_cog(Roles(bot))