import discord
from discord.ext import commands
from ..utils import Uptime #Dataclasses
import os
import colorlog
from logging import DEBUG, Logger
import platform #For platform information
from datetime import datetime #For uptime calculation
from datetime import timezone #For uptime calculation
from discord.http import handle_message_parameters
from aiohttp import ClientSession
from ..secrets import Info
from ..database import DatabaseManager


class Luna(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(Info.PREFIX, intents=intents, owner_ids=Info.OWNER_IDS, options=Info.OPTIONS)
    

    async def setup_hook(self) -> None:
        # ---------------- Bot Variables ----------------
        self.logger = self.get_logger()
        self._boot_time = datetime.now().astimezone(timezone.utc)
        self.tree.on_error = self.on_app_command_error
        # -----------------------------------------------

        # Database Setup
        self.db = DatabaseManager()
        await self.db.setup()

        # --------------------------------

        if Info.CLEAR_APP_COMMANDS:
            self.tree.clear_commands(guild=discord.Object(Info.GUILD_ID))

        if Info.AUTO_LOAD_EXTENSIONS_FROM and Info.FORMATTED_EXTENSIONS_PATH:
            await self.auto_load_extensions()
        
        if Info.AUTO_SYNC_APP_COMMANDS:
            self.tree.copy_global_to(guild=discord.Object(Info.GUILD_ID))
            await self.tree.sync()
            
    
    # Auto extension un/re/loader from a directory
    async def auto_load_extensions(self) -> bool | None:
        [await self.load_extension(f"{Info.FORMATTED_EXTENSIONS_PATH}{file[:-3]}") for file in os.listdir(Info.AUTO_LOAD_EXTENSIONS_FROM) if file.endswith(".py") and not file.startswith("_")]
    
    async def auto_unload_extensions(self) -> None:
        [await self.unload_extension(f"{Info.FORMATTED_EXTENSIONS_PATH}{file[:-3]}") for file in os.listdir(Info.AUTO_LOAD_EXTENSIONS_FROM) if file.endswith(".py") and not file.startswith("_")]
    
    async def auto_reload_extensions(self) -> None:
        await self.auto_unload_extensions()
        await self.auto_load_extensions()
    # -----------------------------------------------

    #Color Logger
    def get_logger(self) -> Logger:
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)s: %(name)s : %(message)s'))
        logger = colorlog.getLogger(self.user.name)
        logger.addHandler(handler)
        logger.setLevel(DEBUG)
        return logger
    
    # ------------------ EVENT -----------------

    async def on_ready(self) -> None:
        app_commands_groups = self.tree.get_commands()
        self.logger.info("%s is connected to Shard ID %s", self.user, self.shard_id)
        self.logger.info("Application ID: %s", self.user.id)
        self.logger.info("Platform: %s", platform.system())
        self.logger.info("Boot Time (UTC): %s", self._boot_time)
        if Info.AUTO_SYNC_APP_COMMANDS:
            self.logger.info("App Commands/Groups Synced: %s", len(app_commands_groups))
            self.logger.info("App Commands/Groups : %s", ", ".join(group.name for group in app_commands_groups))
        else:
            self.logger.critical("Please enable AUTO_SYNC_APP_COMMANDS in secrets.py to sync app commands/groups")
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> discord.InteractionResponse | None:
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            return await interaction.response.send_message(f"Slow Down! Retry after **{error.retry_after:.2f}** seconds", ephemeral=True)
        
        if isinstance(error, discord.app_commands.MissingPermissions):
            return await interaction.response.send_message("You do not have the required permissions to run this command", ephemeral=True)
        
        if isinstance(error, discord.app_commands.BotMissingPermissions):
            return await interaction.response.send_message("I do not have the required permissions to run this command", ephemeral=True)

        self.logger.error(error)


    # ------------------ BOT UTILS -----------------
    @property
    def uptime(self) -> Uptime:
        _upt = int((datetime.now().astimezone(timezone.utc) - self._boot_time).total_seconds())
        hours, remainder = divmod(_upt, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        return Uptime(days, hours, minutes, seconds)


    async def getch_user(self, user_id: int) -> discord.User:
        return self.get_user(user_id) or await self.fetch_user(user_id)
    
    async def getch_guild(self, guild_id: int) -> discord.Guild:
        return self.get_guild(guild_id) or await self.fetch_guild(guild_id)
    
    async def getch_channel(self, channel_id: int) -> discord.TextChannel | discord.VoiceChannel:
        return self.get_channel(channel_id) or await self.fetch_channel(channel_id)

    async def getch_member(self, guild_id: int, member_id: int) -> discord.Member:
        guild = await self.getch_guild(guild_id)
        return guild.get_member(member_id) or await guild.fetch_member(member_id)
    
    async def getch_role(self, guild_id: int, role_id: int) -> discord.Role | None:
        guild = await self.getch_guild(guild_id)
        if (role:=guild.get_role(role_id)):
            return role
        role = [role for role in guild.roles if role.id==role_id]
        if role:
            return role[0]
        
    async def fetch_message(self, channel_id: int, message_id: int) -> discord.Message: 
        channel = await self.getch_channel(channel_id)
        return await channel.fetch_message(message_id)
    

    async def send_message(self, channel_id: int, content: str, **kwargs):
        params = handle_message_parameters(content, **kwargs)
        await self.http.send_message(channel_id, params=params)

    async def make_ready(self) -> None:
        async with ClientSession() as http_client:
            self.http_client = http_client
            await self.start(Info.TOKEN)
    
    def run(self) -> None:
        import asyncio
        asyncio.run(self.make_ready())