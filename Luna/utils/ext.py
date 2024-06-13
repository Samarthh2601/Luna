from discord import app_commands
import discord
from .dtclasses import IDs
from discord import ui
from datetime import datetime, timedelta
from .dtclasses import MessageContent, Record

def make_app_choices(choices: dict):
    return [app_commands.Choice(name=k, value=v) for k, v in choices.items()]

def get_ids_from_link(link: str) -> IDs | None:
    if len(link) == 88 and not link.isdigit() and link.startswith("https://discord.com/channels/"):   
        _link = link.split("/")
        return IDs(int(_link[-3]), int(_link[-2]), int(_link[-1]))
    elif link.isdigit() and len(link) == (19):
        return IDs(None, None, int(link))
    else:
        return None

class BookmarkView(ui.View):
    def __init__(self, embed: discord.Embed, *, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.embed = embed
        self.timeout = timeout

    @ui.button(label="Copy", style=discord.ButtonStyle.green)
    async def recopy(self, inter: discord.Interaction, button: ui.Button) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        try:
            await inter.user.send(embed=self.embed)
            await inter.edit_original_response(content="Successfully replicated the message to your DMs!")
        except discord.Forbidden:
            self.message = await inter.edit_original_response(content="Your DMs are disabled! Enable your DMs and click me again!")

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
        self.stop()


def get_current_tracking_ftstring(records: list[Record] | Record, ft_string=False):
    if ft_string is True:
        if isinstance(records, list):
            return "\n- ".join([f"<https://discord.com/channels/{message.guild_id}/{message.channel_id}/{message.message_id}> ({message.message_id})" for message in records])
        return f"<https://discord.com/channels/{records.guild_id}/{records.channel_id}/{records.message_id}> ({records.message_id})"
    
    if isinstance(records, list):
            return "\n- ".join([f"<https://discord.com/channels/{message.guild_id}/{message.channel_id}/{message.message_id}>" for message in records])
    return f"<https://discord.com/channels/{records.guild_id}/{records.channel_id}/{records.message_id}>"

async def get_message_assets(message: discord.Message) -> MessageContent:
    ret = MessageContent()
    if message.content:
        ret.content = message.content

    if message.attachments:
        attachment = message.attachments[0]
        ret.file_url = attachment.url

    if message.embeds:
        embed = message.embeds[0]
        ret.embed = True
        ret.embed_title = "No Title" if embed.title is None else embed.title
        ret.embed_description = "No Description" if embed.description is None else embed.description
        ret.embed_content = f"**Title**: {ret.embed_title}\n**Description**: {ret.embed_description}"

    return ret

def generate_timestamp(dt: datetime = None, *, style: str = "f", weeks: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0) -> str:
    if dt is None:
        dt = datetime.utcnow()
    return discord.utils.format_dt(dt + timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds), style=style)

