import discord
from dataclasses import dataclass
from typing import Iterable, Any

@dataclass
class Bank:
    user_id: int
    wallet: int
    bank: int

@dataclass
class Embed:
    embed: bool = False
    embed_title: str = None
    embed_description: str = None
    embed_content: str = None

@dataclass
class MessageContent(Embed):
    content: str = None
    file_url: str = None

@dataclass
class Record:
    message_id: int
    user_id: int
    guild_id: int
    channel_id: int=None
    dm_id: int=None
    dm_channel_id: int=None

@dataclass
class Rank:
    user_id: int
    guild_id: int
    experience: int = 10
    level: int = 1

@dataclass
class Uptime:
    days: int
    hours: int
    minutes: int
    seconds: int

@dataclass
class IDs:
    guild_id: int
    channel_id: int
    message_id: int

@dataclass
class Settings:
    TOKEN: str
    OWNER_IDS: Iterable
    PREFIX: str
    GUILD_ID: int = None
    INTENTS: discord.Intents = None
    
    AUTO_SYNC_APP_COMMANDS: bool = False
    CLEAR_APP_COMMANDS: bool = False
    AUTO_LOAD_EXTENSIONS_FROM: str = None
    FORMATTED_EXTENSIONS_PATH: str = None
    OPTIONS: Any = None

    def enable_all_intents(self) -> discord.Intents:
        self.INTENTS = discord.Intents.all()
        return self.INTENTS
    