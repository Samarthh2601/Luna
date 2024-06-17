import discord
from discord.ext import commands
from discord import app_commands, Interaction
import random
import asyncio

from ..core import Luna


class Economy(commands.GroupCog, name="economy"):
    def __init__(self, bot: Luna):
        self.bot = bot

    async def cog_check(self, inter: Interaction) -> bool:
        if inter.user.bot:
            return False
        return True

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, inter: Interaction, user: discord.User=None) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)

        user = user or inter.user
        user_ = await self.bot.db.economy.create(user.id)

        embed = discord.Embed(title="Balance", description=f"Wallet: **{user_.wallet}**\nBank:**{user_.bank}**").set_thumbnail(url=inter.user.display_avatar.url)

        await inter.edit_original_response(embed=embed)
    
    @app_commands.command(name="deposit", description="Deposit money into your bank")
    async def deposit(self, inter: Interaction, amount: int) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)

        user = await self.bot.db.economy.create(inter.user.id)

        if amount > user.wallet:
            return await inter.edit_original_response(content="You don't have enough money to deposit")

        await self.bot.db.economy.update(inter.user.id, wallet=user.wallet - amount, bank=user.bank + amount)

        embed = discord.Embed(title="Deposited", description=f"Deposited **{amount}** into your bank").set_thumbnail(url=inter.user.display_avatar.url).add_field(name="New Wallet Balance", value=user.wallet-amount, inline=False).add_field(name="New Bank Balance", value=user.bank+amount, inline=False)

        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="withdraw", description="Withdraw money from your bank")
    async def withdraw(self, inter: Interaction, amount: int) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)

        user = await self.bot.db.economy.create(inter.user.id)

        if amount > user.bank:
            return await inter.edit_original_response(content="You don't have enough money to withdraw")

        await self.bot.db.economy.update(inter.user.id, wallet=user.wallet + amount, bank=user.bank - amount)

        embed = discord.Embed(title="Withdrawn", description=f"Withdrawn **{amount}** from your bank").set_thumbnail(url=inter.user.display_avatar.url).add_field(name="New Wallet Balance", value=user.wallet+amount, inline=False).add_field(name="New Bank Balance", value=user.bank-amount, inline=False)

        await inter.edit_original_response(embed=embed)


    @app_commands.command(name="transfer", description="Transfer money to another user")
    async def transfer(self, inter: Interaction, user: discord.User, amount: int) -> None | discord.InteractionResponse:
        await inter.response.defer(thinking=True)

        if user.bot:
            return await inter.edit_original_response(content="You can't transfer money to a bot")

        if user.id == inter.user.id:
            return await inter.edit_original_response(content="You can't transfer money to yourself")

        sender = await self.bot.db.economy.create(inter.user.id)
        receiver = await self.bot.db.economy.create(user.id)

        if amount > sender.wallet:
            return await inter.edit_original_response(content="You don't have enough money to transfer")

        await self.bot.db.economy.update(inter.user.id, wallet=sender.wallet - amount)
        await self.bot.db.economy.update(user.id, wallet=receiver.wallet + amount)

        embed = discord.Embed(title="Transferred", description=f"Transferred **{amount}** to {user.mention}").set_thumbnail(url=inter.user.display_avatar.url).add_field(name="New Wallet Balance", value=sender.wallet-amount, inline=False)

        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="leaderboard", description="Check the leaderboard")
    async def leaderboard(self, inter: Interaction) -> discord.InteractionResponse | None:
        await inter.response.defer(ephemeral=True, thinking=True)

        all_records = await self.bot.db.economy.all_records()

        if not all_records:
            return await inter.edit_original_response(content="No records found")

        all_records.sort(key=lambda x: x.wallet, reverse=True)

        embed = discord.Embed(title="Leaderboard (Net)", description="\n".join([f"{idx+1}. <@{record.user_id}> - {record.wallet + record.bank}" for idx, record in enumerate(all_records[:10])]))

        await inter.edit_original_response(embed=embed)

    @app_commands.checks.cooldown(1, 30)
    @app_commands.command(name="beg", description="Beg for Coins!")
    async def beg(self, inter: Interaction) -> discord.InteractionResponse | None:
        await inter.response.defer(ephemeral=True, thinking=True)
        c = random.randint(1, 2)
        if c == 1:
            return await inter.edit_original_response(content="Go find a job or something, good for nothing.")
        user_data = await self.bot.db.economy.create(inter.user.id)
        random_money = random.randint(1, 199)
        await inter.edit_original_response(content=f"You really got **{random_money}** Luna Coins, lucky you! You now have **{user_data.wallet+random_money}** Luna Coins in your wallet!")
        return await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet+random_money)    
       
    @app_commands.checks.cooldown(1, 30)
    @app_commands.command(name="search", description="Search for a few Luna Coins, maybe")
    async def search(self, inter: Interaction) -> discord.InteractionResponse | None:
        await inter.response.defer(ephemeral=True, thinking=True)
        data = await self.bot.db.economy.create(inter.user.id)
        c = random.randint(1, 4)
        await inter.edit_original_response(content="Searching...")
        await asyncio.sleep(2)
        if c == 1 or c == 2:
            return await inter.edit_original_response(content="You found nothing!")
        if c == 3:
            await self.bot.db.economy.update(inter.user.id, wallet=data.wallet-500)
            return await inter.edit_original_response(content="The Luna Police caught you and charged you **500** Luna Coins...")
        r_money = random.randint(100, 499)
        await self.bot.db.economy.update(inter.user.id, wallet=data.wallet+r_money)
        return await inter.edit_original_response(content=f"Lucky you, found {r_money} Luna Coins! You now have {data.wallet+r_money} Luna Coins in your wallet!")

    @app_commands.checks.cooldown(1, 3600)
    @app_commands.command(name="rob", description="Rob another robber (User)!")
    async def rob_user(self, inter: Interaction, member: discord.User) -> discord.InteractionResponse | None:
        await inter.response.defer(thinking=True)
        user_data = await self.bot.db.economy.create(inter.user.id)
        member_data = await self.bot.db.economy.create(member.id)
        if member_data.wallet < 500:
            return await inter.edit_original_response(content=f"**{member}** doesn't even have 500 Luna Coins, not worth it.")
        if not user_data:
            return await inter.edit_original_response(content="You do not have an account yet! Run `/create_account` to create one!")
        if user_data.wallet < 500:
            return await inter.edit_original_response(content="You must have 500 Luna Coins in your wallet to rob others!")
        c = random.randint(1, 4)
        if c == 4:
            return await inter.edit_original_response(content="You came back empty-handed...how sad.")
        elif c == 3:
            rc = random.randint(1, user_data.wallet)
            await inter.edit_original_response(content=f"**{member}** caught you while you were robbing them and stole {rc} Luna Coins from you! Your total wallet balance is now **{user_data.wallet-rc}**!")
            await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet-rc)
            await self.bot.db.economy.update(member.id, wallet=member_data.wallet+rc)
        elif c == 2 or c == 1:
            rc = random.randint(1, member_data.wallet)
            await inter.edit_original_response(content=f"You stole {rc} Luna Coins from **{member}**! Your total wallet balance is now **{user_data.wallet+rc}**!")
            await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet+rc)
            await self.bot.db.economy.update(member.id, wallet=member_data.wallet-rc)

    @app_commands.checks.cooldown(1, 7200)
    @app_commands.command(name="heist", description="Heist the bank of a member!")
    async def heist_(self, inter: Interaction, member: discord.Member):
        await inter.response.defer(thinking=True)
        user_data = await self.bot.db.economy.create(inter.user.id)
        if not user_data:
            return await inter.edit_original_response(content="You do not have an account yet! Run `/create_account` to create one!")
        member_data = await self.bot.db.economy.create(inter.user.id)
        if member_data.bank < 1000:
            return await inter.edit_original_response(content=f"**{member}** isn't worth it. They don't even have 1000 Dark Coins in their bank.")
        c = random.randint(1, 4)
        if c == 4 or c == 2:
            return await inter.edit_original_response(content="You came back empty-handed...how sad.")
        elif c == 3:
            rc = random.randint(1, user_data.bank)
            await inter.edit_original_response(content=f"**{member}** caught you while you were robbing them and stole {rc} Dark Coins from you! Your total bank balance is now **{user_data.bank-rc}**!")
            await self.bot.db.economy.update(inter.user.id, bank=user_data.bank-rc)
            await self.bot.db.economy.update(member.id, bank=member_data.bank+rc)
        elif c == 1:
            rc = random.randint(1, member_data.bank)
            await inter.edit_original_response(content=f"You stole {rc} Dark Coins from **{member}**! Your total bank balance is now **{user_data.bank+rc}**!")
            await self.bot.db.economy.update(inter.user.id, bank=user_data.bank+rc)
            await self.bot.db.economy.update(member.id, bank=member_data.bank-rc)

    @app_commands.checks.cooldown(1, 30)
    @app_commands.choices(side=[app_commands.Choice(name="Heads", value="heads"), app_commands.Choice(name="Tails", value="tails")])
    @app_commands.command(name="coinflip", description="Flip a coin and get more coins or lost them.")
    async def cf(self, inter: Interaction, amount: int, side: str):
        await inter.response.defer(ephemeral=True, thinking=True)
        user_data = await self.bot.db.economy.create(inter.user.id)
        if not user_data:
            return await inter.edit_original_response(content="You do not have an account yet! Run `/create_account` to create one!")
        if amount > user_data.wallet:
            return await inter.edit_original_response(content="The amount you're trying to bet is more than your wallet balance.")

        c = random.choice(["heads", "tails"])
        await inter.edit_original_response(content="Flipping a coin for ya...")
        if side.lower() == c:
            await inter.edit_original_response(content=f"You won! Your wallet balance is now **{user_data.wallet+amount*2}**!")
            return await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet+amount*2)

        await inter.edit_original_response(content=f"You lost. You wallet balance is now **{user_data.wallet-amount}**!")
        await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet-amount)

    @app_commands.checks.cooldown(1, 60)
    @app_commands.command(name="bet", description="Bet your coins for greater amounts or lose it!")
    async def bet_coins(self, inter: Interaction, amount: int):
        await inter.response.defer(ephemeral=True, thinking=True)
        user_data = await self.bot.db.economy.create(inter.user.id)
        if not user_data:
            return await inter.edit_original_response(content="You do not have an account yet! Run `/create_account` to create one!")
        if amount > user_data.wallet:
            return await inter.edit_original_response(content="The amount you're trying to bet is more than your wallet balance.")

        c = random.randint(1, 4)
        if c == 1 or c == 2 or c == 3:
            await inter.edit_original_response(content=f"You lost! Your wallet balance is now **{user_data.wallet-amount}**")
            return await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet-amount)
        await inter.edit_original_response(content=f"You won! Your wallet balance is now **{user_data.wallet+(amount*5)}**")
        await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet+(amount*5))
        
    @app_commands.checks.cooldown(1, 30)
    @app_commands.choices(number=[app_commands.Choice(name=str(i), value=i) for i in range(1, 7)])
    @app_commands.command(name="roll", description="Roll the dice and earn coins!")
    async def roll_(self, inter: Interaction, number: int):
        await inter.response.defer(ephemeral=True, thinking=True)
        user_data = await self.bot.db.economy.create(inter.user.id)
        if not user_data:
            return await inter.edit_original_response(content="You do not have an account yet! Run `/create_account` to create one!")    
        c = random.randint(1, 6)
        if c != number:
            return await inter.edit_original_response(content=f"The dice rolled to **{c}** but you chose the number **{number}**")
        await inter.edit_original_response(content=f"You won! Your wallet balance is now **{user_data.wallet+200}**")
        await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet+200)

    @app_commands.checks.cooldown(1, 45)
    @app_commands.command(name="slots", description="Play the Slots minigame and earn coins!")    
    async def slots(self, inter: Interaction, amount: int):
        await inter.response.defer(ephemeral=True, thinking=True)
        user_data = await self.bot.db.economy.create(inter.user.id)
        if not user_data:
            return await inter.edit_original_response(content="You do not have an account yet! Run `/create_account` to create one!")
        if amount > user_data.wallet:
            return await inter.edit_original_response(content="The amount you're trying to bet is more than your wallet balance.")

        opts = [random.choice([":strawberry:", ":apple:", ":mango:"]) for _ in range(3)]    
        if opts[0] == opts[1] and opts[0] == opts[2]:
            await inter.edit_original_response(content=f"{' | '.join(opts)}, You won! Your wallet balance is now **{user_data.wallet+(amount*3)}**")
            return await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet+(amount*3))
        await inter.edit_original_response(content=f"{' | '.join(opts)}, You lost! Your wallet balance is now **{user_data.wallet-amount}**!")
        await self.bot.db.economy.update(inter.user.id, wallet=user_data.wallet-amount)

async def setup(bot: Luna) -> None:
    await bot.add_cog(Economy(bot))