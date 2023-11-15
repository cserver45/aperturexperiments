"""Cog for economy system."""
import asyncio
import random
import secrets
from copy import deepcopy
from typing import Any, List, Optional, Tuple, Union

from colorama import Back, Style
from discord import Client, Colour, Embed, Message, User
from discord.ext import commands, tasks
from discord.ext.commands import (Cog, Context,
                                   MemberConverter, command)

banned_commands = ("deposit", "withdraw", "balance", "send", "shop", "bag", "badges")

phrases = ("gib me money", "free money", "noooooooo")


class Economy(Cog):
    """Economy Cog parent class."""

    __slots__ = ("bot", "db")

    def __init__(self, bot: Client) -> None:
        """Init function."""
        self.bot = bot
        self.db = bot.db

    @Cog.listener()
    async def on_command_completion(self, ctx: Context) -> None:
        """Called when a command is completed sucessfully."""
        try:
            if ctx.command.cog.qualified_name == "Economy" and ctx.command.name not in banned_commands:
                chance = secrets.randbelow(10)
                if chance in range(2):
                    channel = ctx.channel
                    phrase = random.choice(phrases)

                    def check(m: Message) -> bool:
                        return bool(m.author == ctx.message.author and m.channel == channel and m.content == phrase)

                    try:
                        await ctx.send(f"Quick someone dropped their wallet!\nType `{phrase}`")
                        msg = await self.bot.wait_for('message', timeout=50.0, check=check)
                    except asyncio.TimeoutError:
                        await ctx.send('Either no one answered in time, or no one answered correctly.')
                    else:
                        money = random.randrange(1, 500)
                        await self._open_account(ctx, ctx.author)
                        await msg.reply(f'{ctx.author.mention} was first! You earned {money} coins.')
                        await self._update_bank(ctx.author, money)

                else:
                    pass
            else:
                pass
        except AttributeError:
            pass

    @commands.cooldown(1, 3, commands.BucketType.user)
    @hybrid_command(aliases=["bal"])
    async def balance(self, ctx: Context, member: Optional[MemberConverter]) -> None:
        """Check your balance."""
        member = member or ctx.author
        await self._open_account(ctx, member)
        users = await self._get_user_data(member)
        wallet_amt = users['wallet']
        bank_amt = users['bank']

        bembed = Embed(title=f'{member.name}\'s Balance', colour=Colour.green(), timestamp=ctx.message.created_at)
        bembed.add_field(name='Wallet balance:', value=wallet_amt)
        bembed.add_field(name='Bank balance:', value=bank_amt)
        await ctx.send(embed=bembed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @hybrid_command()
    async def beg(self, ctx: Context) -> None:
        """Why would you beg for money?"""
        await self._open_account(ctx, ctx.author)
        user = ctx.author

        earnings = random.randrange(1, 150)

        await ctx.send(f'Someone gave you {earnings} coins.')
        await self._update_bank(user, earnings)

    @hybrid_command(aliases=['with', 'frombank'])
    async def withdraw(self, ctx: Context, amount: Union[str, int]) -> None:
        """Get some of that money you put in the bank back into your wallet."""
        await self._open_account(ctx, ctx.author)

        bal = await self._update_bank(ctx.author)

        if amount in ("all", "max"):
            await self._update_bank(ctx.author, bal[1])
            await self._update_bank(ctx.author, -1 * bal[1], "bank")
            await ctx.send(f'You withdrawed all of your coins ({bal[1]}) from the bank. wallet balance is {bal[0] + bal[1]}')
            return

        amount = int(amount)
        if amount > bal[1]:
            await ctx.send('You don\'t have that much money!')
            return
        elif amount < 0:
            await ctx.send('Amount can\'t be negitive!')
            return

        await self._update_bank(ctx.author, amount)
        await self._update_bank(ctx.author, -1 * amount, "bank")
        await ctx.send(f'You withdrew {amount} coins from the bank.')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @hybrid_command(aliases=['dep', 'savings'])
    async def deposit(self, ctx: Context, amount: Union[str, int]) -> None:
        """Deposit some money into the bank."""
        await self._open_account(ctx, ctx.author)

        bal = await self._update_bank(ctx.author)

        if amount in ("all", "max"):
            await self._update_bank(ctx.author, bal[0], "bank")
            await self._update_bank(ctx.author, -1 * bal[0])
            await ctx.send(f'You deposited all of your coins ({bal[0]}) to the bank. bank balance is {bal[0] + bal[1]}')
            return

        amount = int(amount)
        if amount > bal[0]:
            await ctx.send('You don\'t have that much money!')
            return
        elif amount < 0:
            await ctx.send('Amount can\'t be negitive!')
            return

        await self._update_bank(ctx.author, amount, "bank")
        await self._update_bank(ctx.author, -1 * amount)
        await ctx.send(f'You deposited {amount} coins to the bank.')

    @commands.cooldown(1, 5, commands.BucketType.user)
    @hybrid_command()
    async def send(self, ctx: Context, member: MemberConverter, amount: int) -> None:
        """Give someone some money."""
        await self._open_account(ctx, ctx.author)
        await self._open_account(ctx, member)
        if member.id == int(ctx.author.id):
            await ctx.send("You can't send money to yourself.")
            return

        bal = await self._update_bank(ctx.author)

        amount = int(amount)
        if not member:
            await ctx.send('You need to specify a member!')
            return
        elif amount > bal[1]:
            await ctx.send('You don\'t have that much money!')
            return
        elif amount < 0:
            await ctx.send('Amount can\'t be negitive!')
            return

        await self._update_bank(ctx.author, -1 * amount, "bank")
        await self._update_bank(member, amount, "bank")
        await ctx.send(f'You Gave {amount} coins to {member} from your bank.')

    @commands.cooldown(1, 60, commands.BucketType.user)
    @hybrid_command()
    async def rob(self, ctx: Context, member: MemberConverter) -> None:
        """Rob some money out of someone's wallet."""
        await self._open_account(ctx, ctx.author)
        if member.id in (776987330967240716, 735894171071545484):
            await ctx.send("You can't rob me.")
            return
        else:
            await self._open_account(ctx, member)

        bal = await self._update_bank(member)

        if not member:
            await ctx.send('You need to specify a member!')
            return
        if bal[0] < 100:
            await ctx.send('It\'s not worth it dude.')
            return

        earnings = random.randrange(0, bal[0])

        await self._update_bank(ctx.author, earnings)
        await self._update_bank(member, -1 * earnings)
        await ctx.send(f'You robbed {member} {earnings} coins.')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @hybrid_command()
    async def slots(self, ctx: Context, amount: int) -> None:
        """Play a Slots machine."""
        await self._open_account(ctx, ctx.author)

        bal = await self._update_bank(ctx.author)

        amount = int(amount)
        if amount > bal[0]:
            await ctx.send('You don\'t have that much money!')
            return
        if amount < 0:
            await ctx.send('Amount can\'t be negitive!')
            return

        final = []
        for _ in range(3):
            a = random.choice([':fire:', ':seven:', ':gem:', ':stars:', ':link:', ':8ball:', ':first_place:', ':second_place:', ':third_place:', ':medal:', ':military_medal:'])

            final.append(a)

        em = Embed(title='Slots machine', colour=Colour.orange(), timestamp=ctx.message.created_at)
        em.add_field(name='Results:', value=f'Your Results were: {final[0]}, {final[1]}, {final[2]}', inline=False)
        if final[0] == ':seven:' and final[1] == ':seven:' and final[2] == ':seven:':
            await self._update_bank(ctx.author, 5 * amount)
            em.add_field(name='You won the jackpot!', value=f'You won {5*amount} coins!', inline=False)
            await ctx.send(embed=em)
            return
        elif final[0] == final[1] and final[0] == final[2] and final[1] == final[2]:
            await self._update_bank(ctx.author, 3 * amount)
            em.add_field(name='You won!', value=f'You won {3*amount} coins!', inline=False)
            await ctx.send(embed=em)
            return
        elif final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
            await self._update_bank(ctx.author, 2 * amount)
            em.add_field(name='You won!', value=f'You won {2*amount} coins!', inline=False)
            await ctx.send(embed=em)
            return
        else:
            await self._update_bank(ctx.author, -1 * amount)
            em.add_field(name='You lost', value='Maybe try again?', inline=False)
            await ctx.send(embed=em)

    @hybrid_command()
    async def shop(self, ctx: Context) -> None:
        """See what items are in stock."""
        em = Embed(title="Shop", timestamp=ctx.message.created_at)

        mshop = self.db.shop_data.find().sort("name")

        for item in await mshop.to_list(length=10):
            name = item["name"]
            price = item["price"]
            desc = item["description"]
            em.add_field(name=name, value=f'${price} | {desc}')

        await ctx.send(embed=em)

    @hybrid_command()
    async def badges(self, ctx: Context, user: Optional[User]) -> None:
        """See what badges you currently have."""
        await self._open_account(ctx, user or ctx.author)
        result = await self._check_badges(user or ctx.author)
        em = Embed(title=f"{ctx.author.display_name}\'s Badges",
                   timestamp=ctx.message.created_at,
                   description=result
                   )
        await ctx.send(embed=em)

    @hybrid_command(hidden=True)
    @commands.is_owner()
    async def add_exp(self, ctx: Context, ammount: int = 500, member: MemberConverter = None) -> None:
        """Add coins to someones wallet/bank (Developers only)."""
        if member is None:
            member = ctx.author
        await self._open_account(ctx, member)
        await self._update_bank(member, int(ammount))
        await ctx.send(f'Added {ammount} coins to {member}.')

    @hybrid_command()
    async def buy(self, ctx: Context, item: str, amount: Optional[int]) -> None:
        """Buy something."""
        amount = amount or 1  # stop it mypy
        await self._open_account(ctx, ctx.author)

        res = await self._buy_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
                return

        await ctx.send(f"You just bought {amount} {item}(s).")

    @hybrid_command(aliases=["inv", "inventory"])
    async def bag(self, ctx: Context) -> None:
        """See what you have bought."""
        await self._open_account(ctx, ctx.author)

        em = Embed(title="Bag", timestamp=ctx.message.created_at)

        user_db = await self._get_user_data(ctx.author)
        for item, amt in user_db["inv"].items():
            name = item
            amount = amt

            em.add_field(name=name, value=amount)

        await ctx.send(embed=em)

    @hybrid_command()
    async def sell(self, ctx: Context, item: str, amount: Optional[int]) -> None:
        """Sell something you have in your bag."""
        amount = amount or 1  # mypy shutup already
        await self._open_account(ctx, ctx.author)

        res = await self._sell_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(f"You don't have {amount} {item} in your bag.")
                return
            if res[1] == 3:
                await ctx.send(f"You don't have {item} in your bag.")
                return

        await ctx.send(f"You just sold {amount} {item}(s).")

    @hybrid_command(aliases=('hilow', 'hilo'))
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def highlow(self, ctx: Context, choice: str, bet: Optional[Union[int, float]]) -> None:
        """Bet some money on whether the dice have a high number or a low number.

        The middle point is 7, above 7 is high, below 7 is low.
        **If** you get 7, your bet is multiplied by 5. Otherwise if you win, you get your bet multiplied by 1.2.
        Acceptable choices are `high`, `hi`, `low`, `lo`, `7`, or `seven`.
        """
        bet = bet or 250  # so mypy will shutup
        valid_response = (("low"), ("lo"), ("high"), ("hi"), ("seven"), ("7"))
        if str(choice) not in valid_response:
            await ctx.send("That is not a valid option.")
            return

        await self._open_account(ctx, ctx.author)
        user_db = await self._get_user_data(ctx.author)

        if int(bet) < 1:
            await ctx.send("You can't bet a negative amount of money.")
            return
        if int(bet) > int(user_db["wallet"]):
            await ctx.send("You don't have that much money in your wallet at this time.")
            return

        message = await ctx.send("The dice hit the table and slowly fall into place...")
        old_bet = deepcopy(bet)
        await asyncio.sleep(2)
        result = sum(self._roll_dice())
        if result < 7:
            outcome = ("low", "lo")
        elif result > 7:
            outcome = ("high", "hi")
        else:
            outcome = ("seven", "7")

        msg = f"The outcome was {result} ({outcome[0]})!"

        if result == 7 and outcome[1] == "7" and choice in outcome:
            bet *= 5
            won = True
        elif choice in outcome and result != 7:
            bet *= 1.2
            won = True
        else:
            won = False
            bet *= -1

        await message.edit(content=msg + f"\nYour choice was {choice}. You {'won' if won is True else 'lost'} {old_bet if won is False else int(bet)} coins.")
        await self._update_bank(ctx.author, int(bet))

    @hybrid_command()
    async def dive(self, ctx: Context) -> None:
        """Dive and see what people dropped over boats."""
        await self._open_account(ctx, ctx.author)

        item_amt = await self._check_item_amount(ctx.author, "mask")

        if item_amt <= 0:
            await ctx.send("You have no diving masks in your invintory right now. Go buy some if you actualy want to dive.")
            return

        probability = random.randint(1, 100)

        with_mask = bool(probability > 85)

        if with_mask:
            amt = random.randint(1, 1500)
            await self._update_bank(ctx.author, amt)
            await ctx.send(f"Hey look you found some money ({amt} coin(s)), and a free mask.")
            return
        elif probability >= 35:
            amt = random.randint(2, 750)
            await self._update_bank(ctx.author, amt)
            await self._change_user_fields(ctx.author, "inv.mask", (item_amt - 1))
            await ctx.send(f"Looks like you found a small bit of money ({amt} coins).")
            return
        else:
            await self._change_user_fields(ctx.author, "inv.mask", (item_amt - 1))
            await ctx.send("Looks like you only found rocks... :rock:")
            return

    """@command(aliases=["lb", "glb", "leaders"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def leaderboard(self, ctx: Context, field: str) -> None:
        Show the leaderboard for the entire bot.
        result = await self.get_lb(ctx, ctx.author, field)
        await ctx.send(embed=result)"""

    # economy stuff backend

    @staticmethod
    def _roll_dice() -> Tuple:
        """Roll 2 dice."""
        return random.randint(1, 6), random.randint(1, 6)

    async def _open_account(self, ctx: Context, user: User) -> bool:
        """Register an account in the db."""
        users = await self._get_user_data(user)
        if users is not None:
            return False

        await self.db.economy_data.insert_one({"userid": str(user.id), "wallet": 100, "bank": 100, "inv": {"watch": 0}})
        await ctx.send(f"{user.name} has been registired in the economy system.")
        return True

    async def _update_bank(self, user: User, change: int = 0, mode: str = "wallet") -> List[int]:
        """Update some part of the user's bank info."""
        change = int(change)
        if change != 0:
            old_document = await self._get_user_data(user)
            new_num = old_document[mode] + int(change)
            await self._change_user_fields(user, mode, new_num)
        updated_data = await self._get_user_data(user)
        bal = [updated_data["wallet"], updated_data["bank"]]

        return bal

    async def _get_user_data(self, user: User) -> Any:
        """Get data that is stored about that user. Returns None if that user does not exist in the db."""
        return await self.db.economy_data.find_one({"userid": str(user.id)})

    async def _change_user_fields(self, user: User, field: str, value: Union[str, int, dict]) -> bool:
        """Change a value in the database."""
        try:
            await self.db.economy_data.update_one({'userid': str(user.id)}, {'$set': {field: value}})
            return True
        except ValueError:
            return False

    async def _check_item_amount(self, user: User, name: str) -> int:
        """Does a user own this item?"""
        user_db = await self._get_user_data(user)

        try:
            return int(user_db['inv'][str(name)])
        except KeyError:
            return 0

    async def _buy_this(self, user: User, item_name: str, amount: int) -> List[Union[bool, str, int]]:
        """Buy something."""
        item_name = item_name.lower()
        mshop = await self.db.shop_data.find_one({"name": str(item_name.capitalize())})

        if mshop is None:
            return [False, 1]

        price = mshop["price"]
        cost = price * amount
        bal = await self._update_bank(user)

        if bal[0] < int(cost):
            return [False, 2]

        user_db = await self._get_user_data(user)

        if item_name in user_db["inv"]:
            new_amt = int(user_db["inv"][item_name]) + amount
            await self._change_user_fields(user, f"inv.{item_name}", int(new_amt))
        else:
            await self._change_user_fields(user, f"inv.{item_name}", int(amount))

        await self._update_bank(user, cost * -1, "wallet")

        return [True, "Worked"]

    async def _sell_this(self, user: User, item_name: str, amount: int, price: int = 0) -> List[Union[bool, int, str]]:
        """Sell something."""
        price = price or 0  # mypy sigh
        item_name = item_name.lower()
        mshop = await self.db.shop_data.find_one({"name": str(item_name.capitalize())})

        if mshop is None:
            return [False, 1]

        cost = price * amount

        item_amt = await self._check_item_amount(user, item_name)

        if item_amt <= 0:
            return [False, 3]
        elif item_amt - amount < 0:
            return [False, 2]
        else:
            new_amt = item_amt - amount
            await self._change_user_fields(user, f"inv.{item_name}", int(new_amt))
            await self._update_bank(user, cost, "wallet")

        return [True, "Worked"]

    async def _check_badges(self, user: User) -> str:
        """See what badges the user has."""
        user_db = await self._get_user_data(user)
        badge_text = ""
        try:
            if user_db["badges"]:
                for badge in user_db["badges"]:
                    badge_text += f"{badge} Badge\n"
                    return badge_text
            else:
                return "You have no Badges."
        except KeyError:
            await self._change_user_fields(user, "badges", {})

        return "You have no Badges."

    """async def get_lb(self, ctx: Context, user: User, field: str) -> Embed:
        Return an embed with the global leaderboard.
        users_db = self.db.economy.find().sort(field, -1)

        e = Embed(title=f"Global Leaderboard by {field}", timestamp=ctx.message.created_at)
        e.set_footer(text=f"Requested By: {ctx.author.name}", icon_url=ctx.author.avatar_url)
        i = 1

        async for db_user in users_db:
            temp_user = ctx.guild.get_member(db_user["userid"])
            temp_bank = db_user["bank"]
            if db_user["userid"] == user.id:
                e.add_field(name=f"{i}: **{temp_user.name}**", value=f"**${temp_bank}**", inline=False)
            else:
                e.add_field(name=f"{i}: {temp_user.name}", value=f"${temp_bank}", inline=False)
            i += 1

            if i == 11:
                break

        return e"""


async def setup(bot: Client) -> None:
    """Setup Function for economy cog."""
    await bot.add_cog(Economy(bot))
