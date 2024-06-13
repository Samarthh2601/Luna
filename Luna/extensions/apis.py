import discord
from discord import app_commands
from discord.ext import commands
import jokeapi
from ..core import Luna


class APIs(commands.GroupCog, name='api'):
    def __init__(self, bot: Luna):
        self.bot = bot

    @app_commands.command(name="dictionary", description="Get the meaning of a word!")
    async def dictionary(self, inter: discord.Interaction, word: str):
        await inter.response.defer(ephemeral=True, thinking=True)
        resp = await self.bot.http_client.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")

        if resp.status != 200:
            return await inter.edit_original_response(content="Could not find that word!")

        data = (await resp.json())[0]

        embed = discord.Embed(title=data['word'], description=f"{data['phonetics'][1]['text']}\nYou can listen to the pronunciation [here]({data['phonetics'][0]['audio']}) (if applicable)", colour=inter.user.colour).add_field(name="Part of Speech", value=data['meanings'][0]['partOfSpeech'], inline=False).add_field(name="More Links", value="\n".join(data['sourceUrls']), inline=False).add_field(name="Definitions", value="\n- ".join([definition['definition'] for definition in data['meanings'][0]['definitions']]))
        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="quote", description="Get a quote!")
    async def quote(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True, thinking=True)
        resp = await self.bot.http_client.get("https://zenquotes.io/api/random")
        if resp.status != 200:
            return await inter.edit_original_response(content="Could not get a quote!")
        data = (await resp.json())[0]
        await inter.edit_original_response(content="**" + data['q'] + "**" + " - " + "*" + data['a'] + "*")

    @app_commands.command(name="joke", description="Get a joke!")
    async def joke(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True, thinking=True)
        j = await jokeapi.Jokes()
        raw_joke = await j.get_joke(safe_mode=True)

        embed = discord.Embed(title="J.O.K.E", description="", color=inter.user.colour)

        if raw_joke['type'] == "single":
            embed.description = raw_joke['joke']
        else:
            embed.description = f"{raw_joke['setup']}\n{raw_joke['delivery']}"
        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="dad_joke", description="Get a quote!")
    async def dad_joke(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True, thinking=True)
        resp = await self.bot.http_client.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
        if resp.status != 200:
            return await inter.edit_original_response(content="Could not get a dad joke!")
        data = (await resp.json())
        await inter.edit_original_response(content=data['joke'])

    
    @app_commands.command(name="fact", description="Get a fact!")
    async def fact(self, inter: discord.Interaction): 
        await inter.response.defer(ephemeral=True, thinking=True)
        resp = await self.bot.http_client.get("https://uselessfacts.jsph.pl/random.json?language=en")
        if resp.status != 200:
            return await inter.edit_original_response(content="Could not get a fact!")
        data = (await resp.json())
        await inter.edit_original_response(content=data['text'])
    
async def setup(bot: Luna):
    await bot.add_cog(APIs(bot))