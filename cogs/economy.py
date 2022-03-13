"""Cog for economy system."""
import asyncio
import random
import secrets
from copy import deepcopy
from typing import Any, List, Optional, Tuple, Union

from colorama import Back, Style
from discord import Client, Colour, Embed, Message, Reaction, User
from discord.ext import commands, tasks
from discord.ext.commands import (Cog, CommandOnCooldown, Context,
                                   MemberConverter, command)

banned_commands = ("deposit", "withdraw", "balance", "send", "shop", "bag")

phrases = ("gib me money", "free money", "noooooooo")


class Economy(Cog):
    """Economy Cog parent class."""

    def __init__(self, bot: Client) -> None:
        """Init function."""
        self.bot = bot
        self.db = bot.db

    @Cog.listener()
    async def on_ready(self) -> None:
        """Called when cog is loaded and ready."""
        # pylint: disable=E1101
        if self.bot.argus.token == "protoken":
            self.do_econ_raffle.start()

        # pylint: enable=E1101
        print(Back.GREEN + Style.BRIGHT + "Economy Cog loaded." + Style.RESET_ALL)

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
                        await ctx.send(f"Quick someone dropped there wallet!\nType `{phrase}`")
                        msg = await self.bot.wait_for('message', timeout=50.0, check=check)
                    except asyncio.TimeoutError:
                        await ctx.send('Either no one answered in time, or no one answered correctly.')
                    else:
                        money = random.randrange(1, 500)
                        await self.open_account(ctx, ctx.author)
                        await msg.reply(f'{ctx.author.mention} was first! You earned {money} coins.')
                        await self.update_bank(ctx.author, money)

                else:
                    pass
            else:
                pass
        except AttributeError:
            pass

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        """Called when an error is encounted with the bot."""
        if isinstance(error, CommandOnCooldown):
            await ctx.send(f"{ctx.command.name} is on cooldown. You can use it again in {round(error.retry_after)} seconds.")

    # economy raffle stuff
    @tasks.loop(hours=12)
    async def do_econ_raffle(self) -> None:
        """Do the economy raffle every 12 hours."""
        guild = self.bot.get_guild(843208429409402920)
        prize = random.randint(1, 1000)
        winner = random.choice(guild.members)
        while winner.bot:
            winner = random.choice(guild.members)
        channel = guild.get_channel(861725677367197707)
        await self.open_account(channel, winner)
        await self.update_bank(winner, prize)
        await channel.send(f"{winner.name} has won {prize} coins.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @command(aliases=["bal"])
    async def balance(self, ctx: Context, member: Optional[MemberConverter]) -> None:
        """Check your balance."""
        member = member or ctx.author
        await self.open_account(ctx, member)
        users = await self.get_user_data(member)
        wallet_amt = users['wallet']
        bank_amt = users['bank']

        bembed = Embed(title=f'{member.name}\'s Balance', colour=Colour.green(), timestamp=ctx.message.created_at)
        bembed.add_field(name='Wallet balance:', value=wallet_amt)
        bembed.add_field(name='Bank balance:', value=bank_amt)
        await ctx.send(embed=bembed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @command()
    async def beg(self, ctx: Context) -> None:
        """Why would you beg for money?"""
        await self.open_account(ctx, ctx.author)
        user = ctx.author

        earnings = random.randrange(1, 150)

        await ctx.send(f'Someone gave you {earnings} coins.')
        await self.update_bank(user, earnings)

    @command(aliases=['with', 'frombank'])
    async def withdraw(self, ctx: Context, amount: Union[str, int]) -> None:
        """Get some of that money you put in the bank back into your wallet."""
        await self.open_account(ctx, ctx.author)

        bal = await self.update_bank(ctx.author)

        if amount in ("all", "max"):
            await self.update_bank(ctx.author, bal[1])
            await self.update_bank(ctx.author, -1 * bal[1], "bank")
            await ctx.send(f'You withdrawed all of your coins ({bal[1]}) from the bank. wallet balance is {bal[0] + bal[1]}')
            return

        amount = int(amount)
        if amount > bal[1]:
            await ctx.send('You don\'t have that much money!')
            return
        elif amount < 0:
            await ctx.send('Amount can\'t be negitive!')
            return

        await self.update_bank(ctx.author, amount)
        await self.update_bank(ctx.author, -1 * amount, "bank")
        await ctx.send(f'You withdrew {amount} coins from the bank.')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @command(aliases=['dep', 'savings'])
    async def deposit(self, ctx: Context, amount: Union[str, int]) -> None:
        """Deposit some money into the bank."""
        await self.open_account(ctx, ctx.author)

        bal = await self.update_bank(ctx.author)

        if amount in ("all", "max"):
            await self.update_bank(ctx.author, bal[0], "bank")
            await self.update_bank(ctx.author, -1 * bal[0])
            await ctx.send(f'You deposited all of your coins ({bal[0]}) to the bank. bank balance is {bal[0] + bal[1]}')
            return

        amount = int(amount)
        if amount > bal[0]:
            await ctx.send('You don\'t have that much money!')
            return
        elif amount < 0:
            await ctx.send('Amount can\'t be negitive!')
            return

        await self.update_bank(ctx.author, amount, "bank")
        await self.update_bank(ctx.author, -1 * amount)
        await ctx.send(f'You deposited {amount} coins to the bank.')

    @commands.cooldown(1, 5, commands.BucketType.user)
    @command()
    async def send(self, ctx: Context, member: MemberConverter, amount: int) -> None:
        """Give someone some money."""
        await self.open_account(ctx, ctx.author)
        await self.open_account(ctx, member)
        if member.id == int(ctx.author.id):
            await ctx.send("You can't send money to yourself.")
            return

        bal = await self.update_bank(ctx.author)

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

        await self.update_bank(ctx.author, -1 * amount, "bank")
        await self.update_bank(member, amount, "bank")
        await ctx.send(f'You Gave {amount} coins to {member} from your bank.')

    @commands.cooldown(1, 60, commands.BucketType.user)
    @command()
    async def rob(self, ctx: Context, member: MemberConverter) -> None:
        """Rob some money out of someone's wallet."""
        await self.open_account(ctx, ctx.author)
        if member.id == 776987330967240716 or member.id == 735894171071545484:
            await ctx.send("You can't rob me.")
            return
        else:
            await self.open_account(ctx, member)

        bal = await self.update_bank(member)

        if not member:
            await ctx.send('You need to specify a member!')
            return
        if bal[0] < 100:
            await ctx.send('It\'s not worth it dude.')
            return

        earnings = random.randrange(0, bal[0])

        await self.update_bank(ctx.author, earnings)
        await self.update_bank(member, -1 * earnings)
        await ctx.send(f'You robbed {member} {earnings} coins.')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @command()
    async def slots(self, ctx: Context, amount: int) -> None:
        """Play a Slots machine."""
        await self.open_account(ctx, ctx.author)

        bal = await self.update_bank(ctx.author)

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
            await self.update_bank(ctx.author, 5 * amount)
            em.add_field(name='You won the jackpot!', value=f'You won {5*amount} coins!', inline=False)
            await ctx.send(embed=em)
            return
        elif final[0] == final[1] and final[0] == final[2] and final[1] == final[2]:
            await self.update_bank(ctx.author, 3 * amount)
            em.add_field(name='You won!', value=f'You won {3*amount} coins!', inline=False)
            await ctx.send(embed=em)
            return
        elif final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
            await self.update_bank(ctx.author, 2 * amount)
            em.add_field(name='You won!', value=f'You won {2*amount} coins!', inline=False)
            await ctx.send(embed=em)
            return
        else:
            await self.update_bank(ctx.author, -1 * amount)
            em.add_field(name='You lost', value='Maybe try again?', inline=False)
            await ctx.send(embed=em)

    @command()
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

    """@bot.command(aliases=['cphone', 'phone'])
    async def cellphone(ctx):
        await ctx.send('What do you want to use your phone for (you have 30 seconds)\nOptions:\n`text` Send a message to someone in this server')
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('You didn\'t answer in time, please be quicker next time!')
            return
        else:
            if msg.content == 'text':
                await ctx.send('Message content: (answer in 30 seconds)')
                try:
                    msg2 = await bot.wait_for('message', timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.send('You didn\'t answer in time dummy.')
                    return
                else:
                    await ctx.send('User to dm (again 30 seconds)')
                    try:
                        user = await bot.wait_for('message', timeout=30.0, check=check)
                    except asyncio.TimeoutError:
                        await ctx.send('You didn\'t answer in time dummy.')
                        return
                    #try:
                    print(user)
                    dmuser = user.server.get_member("id")
                    await dmuser.send(msg2)
                    await ctx.send("Sent the message.")"""

    @commands.cooldown(1, 5, commands.BucketType.user)
    @command()
    async def server(self, ctx: Context, how_long: Optional[int]) -> None:
        """Run a game server and make some money."""
        await self.open_account(ctx, ctx.author)

        how_long = how_long or 5  # this is so mypy isin't mad

        user_db = await self.db.economy_data.find_one({'userid': str(ctx.author.id)})

        try:
            if int(user_db["inv"]["server"]) >= 1 and (int(user_db["server_use"]) + 1) <= (int(user_db["inv"]["server"])):

                await self.db.economy_data.update_one({'userid': str(ctx.author.id)}, {'$set': {"server_use": (int(user_db["server_use"]) + 1)}})
                em = Embed(title='What Type of game do you want to host? (You have 20 seconds to react)', colour=Colour.green())
                em.add_field(name='Among us', value='5 coins per minute (:sunglasses:) (must be 5 minutes or longer)')
                # em.add_field(name = 'Minecraft server', value = '7 coins per minute but must be runned for 10 minutes minimum. (:clap:)')
                bot_msg = await ctx.send(embed=em)

                await bot_msg.add_reaction('😎')
                await bot_msg.add_reaction('👏')

                def check(reaction: Reaction, user: User) -> bool:
                    return bool(user == ctx.message.author and str(reaction.emoji) in ['😎', '👏'])

                reaction, _ = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                if reaction.emoji == "😎" and how_long >= 5:
                    await ctx.send(f'Ok, Among us server it is! In {how_long} minutes, you will be given {how_long*5} coins.')
                    await asyncio.sleep(how_long * 60)
                    await ctx.send(f'Done! {how_long*5} coins will be added to your account')
                    await self.update_bank(ctx.author, 5 * how_long)
                    await self.db.economy_data.update_one({'userid': str(ctx.author.id)}, {'$set': {"server_use": (int(user_db["server_use"]) - 1)}})
                    return
                elif reaction.emoji == "👏":
                    await ctx.send("Disabled for now.")

                # elif ctx.message.reactions == '👏':

                else:
                    await ctx.send('Either you didnt select a server in time, or you had too short of a time.')

            else:
                await ctx.send('You dont own anymore servers then what are running right now.')
        except KeyError:
            await ctx.send("You don\'t own any servers.")

    @command(hidden=True)
    @commands.is_owner()
    async def add_exp(self, ctx: Context, ammount: int = 500, member: MemberConverter = None) -> None:
        """Add coins to someones wallet/bank (Developers only)."""
        if member is None:
            member = ctx.author
        await self.open_account(ctx, member)
        await self.update_bank(member, int(ammount))
        await ctx.send(f'Added {ammount} coins to {member}.')

    @command(name="vote", hidden=True)
    async def get_vote_embed(self, ctx: Context) -> None:
        """Show an embed about how many times you've voted, and what rewards you'll get if you do vote."""
        await self.open_account(ctx, ctx.author)
        await self.register_vote(ctx.author.id)

        em = Embed(title=f"{ctx.author.display_name} vote stats.",
                   description="Voting helps promote the bot so others can expieriance what you have.\n\n[Top.gg vote link](https://top.gg/)\n[Fateslist vote link](https://fateslist.xyz/bot/735894171071545484)",
                   timestamp=ctx.message.created_at,
                   color=Colour.green())
        await ctx.send(embed=em)

    @command()
    async def buy(self, ctx: Context, item: str, amount: Optional[int]) -> None:
        """Buy something."""
        amount = amount or 1  # stop it mypy
        await self.open_account(ctx, ctx.author)

        res = await self.buy_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
                return

        await ctx.send(f"You just bought {amount} {item}(s).")

    @command(aliases=["inv", "inventory"])
    async def bag(self, ctx: Context) -> None:
        """See what you have bought."""
        await self.open_account(ctx, ctx.author)
        user = ctx.author

        em = Embed(title="Bag", timestamp=ctx.message.created_at)

        user_db = await self.db.economy_data.find_one({'userid': str(user.id)})
        for item, amt in user_db["inv"].items():
            name = item
            amount = amt

            em.add_field(name=name, value=amount)

        await ctx.send(embed=em)

    @command()
    async def sell(self, ctx: Context, item: str, amount: Optional[int]) -> None:
        """Sell something you have in your bag."""
        amount = amount or 1  # mypy shutup already
        await self.open_account(ctx, ctx.author)

        res = await self.sell_this(ctx.author, item, amount)

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

    @command(aliases=('hilow', 'hilo'))
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

        await self.open_account(ctx, ctx.author)
        user_db = await self.db.economy_data.find_one({'userid': str(ctx.author.id)})

        if int(bet) < 1:
            await ctx.send("You can't bet a negative amount of money.")
            return
        if int(bet) > int(user_db["wallet"]):
            await ctx.send("You don't have that much money in your wallet at this time.")
            return

        message = await ctx.send("The dice hit the table and slowly fall into place...")
        old_bet = deepcopy(bet)
        await asyncio.sleep(2)
        result = sum(self.roll_dice())
        if result < 7:
            outcome = ("low", "lo")
        elif result > 7:
            outcome = ("high", "hi")
        else:
            outcome = ("seven", "7")

        msg = "The outcome was {} ({[0]})!".format(result, outcome)

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
        await self.update_bank(ctx.author, int(bet))

    @command()
    async def dive(self, ctx: Context) -> None:
        """Dive and see what people dropped over boats."""
        await self.open_account(ctx, ctx.author)

        user_db = await self.db.economy_data.find_one({'userid': str(ctx.author.id)})

        try:
            if user_db["inv"]["mask"] <= 0:
                await ctx.send("You have 0 diving masks in your invintory right now. Go buy some if you actualy want to dive.")
                return
        except KeyError:
            await ctx.send("You dont have any diving masks in your invintory at this time. (hint: buy some with `buy mask`)")
            return

        probability = random.randint(1, 100)

        with_mask = bool(probability > 85)

        if with_mask:
            amt = random.randint(1, 1500)
            await self.update_bank(ctx.author, amt)
            await ctx.send(f"Hey look you found some money ({amt} coin(s)), and a free mask.")
            return
        elif probability >= 35:
            amt = random.randint(2, 750)
            await self.update_bank(ctx.author, amt)
            await self.db.economy_data.update_one({"userid": str(ctx.author.id)}, {"$set": {"inv.mask": (user_db["inv"]["mask"] - 1)}})
            await ctx.send(f"Looks like you found a small bit of money ({amt} coins).")
            return
        else:
            await self.db.economy_data.update_one({"userid": str(ctx.author.id)}, {"$set": {"inv.mask": (user_db["inv"]["mask"] - 1)}})
            await ctx.send("Looks like you only found rocks... :rock:")
            return

    # economy stuff backend

    @staticmethod
    def roll_dice() -> Tuple:
        """Roll 2 dice."""
        return random.randint(1, 6), random.randint(1, 6)

    async def register_vote(self, userid: int) -> bool:
        """Check if someone has voted or ran the vote command."""
        user = await self.db.economy_data.find_one({"userid": userid})

        user_voted = user.get("vote") or None

        if not user_voted:
            await self.db.economy_data.update_one({"userid": userid}, {"$set": {"vote.total": 0, "vote.week": 0, "vote.topgg": False, "vote.fateslist": False}})
            return True

        return False

    async def open_account(self, ctx: Context, user: User) -> bool:
        """Register an account in the db."""
        users = await self.get_user_data(user)
        if users is not None:
            return False

        await self.db.economy_data.insert_one({"userid": str(user.id), "wallet": 100, "bank": 100, "inv": {"watch": 0}})
        await ctx.send(f"{user.name} has been registired in the economy system.")
        return True

    async def update_bank(self, user: User, change: int = 0, mode: str = "wallet") -> List[int]:
        """Update some part of the user's bank info."""
        change = int(change)
        coll = self.db.economy_data
        if change != 0:
            old_document = await self.get_user_data(user)
            new_num = old_document[mode] + int(change)
            await coll.update_one({'userid': str(user.id)}, {'$set': {mode: new_num}})
        updated_data = await self.get_user_data(user)
        bal = [updated_data["wallet"], updated_data["bank"]]

        return bal

    async def get_user_data(self, user: User) -> Any:
        """Get data that is stored about that user. Returns None if that user does not exist in the db."""
        return await self.db.economy_data.find_one({"userid": str(user.id)})

    async def buy_this(self, user: User, item_name: str, amount: int) -> List[Union[bool, str, int]]:
        """Buy something."""
        item_name = item_name.lower()
        mshop = await self.db.shop_data.find_one({"name": str(item_name.capitalize())})

        if mshop is None:
            return [False, 1]

        price = mshop["price"]

        cost = price * amount

        bal = await self.update_bank(user)

        if bal[0] < int(cost):
            return [False, 2]

        user_db = await self.get_user_data(user)

        if item_name in user_db["inv"]:
            new_amt = int(user_db["inv"][item_name]) + amount
            await self.db.economy_data.update_one({'userid': str(user.id)}, {'$set': {f"inv.{item_name}": int(new_amt)}})
        else:
            await self.db.economy_data.update_one({"userid": str(user.id)}, {'$set': {f"inv.{item_name}": int(amount)}})

        await self.update_bank(user, cost * -1, "wallet")

        return [True, "Worked"]

    async def sell_this(self, user: User, item_name: str, amount: int, price: int = 0) -> List[Union[bool, int, str]]:
        """Sell something."""
        price = price or 0  # mypy sigh
        item_name = item_name.lower()
        name_ = None
        mshop = self.db.shop_data.find()

        for item in await mshop.to_list(length=20):
            name = item["name"].lower()
            if name == item_name:
                name_ = name
                if price == 0:
                    price = 0.9 * item["price"]
                break

        if name_ is None:
            return [False, 1]

        cost = price * amount

        user_db = await self.db.economy_data.find_one({'userid': str(user.id)})

        if item_name in user_db["inv"]:
            new_amt = int(user_db["inv"][item_name]) - amount
            if new_amt < 0:
                return [False, 2]
            await self.db.economy_data.update_one({'userid': str(user.id)}, {'$set': {f"inv.{item_name}": int(new_amt)}})
        else:
            return [False, 3]

        await self.update_bank(user, cost, "wallet")

        return [True, "Worked"]


def setup(bot: Client) -> None:
    """Setup Function for economy cog."""
    bot.add_cog(Economy(bot))
