"""Fun and games cog."""
from random import choice, randint
from typing import Optional, Literal

from discord import Client, Color, Embed, Message
from discord.ext.commands import Cog, Context, MemberConverter, hybrid_command

# discord.py commands must have self included, even if its not used
# pylint: disable=R0201

class Games(Cog):
    """Parent class."""

    __slots__ = ("bot", "db", "session")

    def __init__(self, bot: Client) -> None:
        """Init Function."""
        self.bot = bot
        self.db = bot.db
        self.session = bot.session

    @hybrid_command(name="flip")
    async def flip(self, ctx: Context, member: Optional[MemberConverter] = None) -> None:
        """Flip a coin. (or a user :o)."""
        if member is not None:
            msg = ""
            if member.id == ctx.bot.user.id:
                member = ctx.author
                msg = ("Yeah right, you cant do it to me.\nWhy don't we try this **instead**.")
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = member.display_name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            await ctx.send(msg + "\n\n" + name[::-1])
        else:
            await ctx.send("*flips a coin and... " + choice(["its HEADS!*", "its TAILS!*"]))

    @hybrid_command(name="rps")
    async def rockps(self, ctx: Context, player_c: Literal["Rock", "Paper", "Scissors"]) -> None:
        """Play Rock Paper Scissors against the bot."""
        user = await self.db.rpstats.find_one({"userid": ctx.author.id})

        if user is None:
            await self.db.rpstats.insert_one({"userid": ctx.author.id, "win": 0, "tie": 0, "lost": 0})
            # refetch the user with updated info
            user = await self.db.rpstats.find_one({"userid": ctx.author.id})

        bot_choice = choice(("Rock", "Paper", "Scissors"))

        cond = {
            ("Rock", "Paper"): False,
            ("Rock", "Scissors"): True,
            ("Paper", "Rock"): True,
            ("Paper", "Scissors"): False,
            ("Scissors", "Rock"): False,
            ("Scissors", "Paper"): True,
        }

        if bot_choice == player_c:
            result = None  # Means its a tie.
        else:
            result = cond[(player_c, bot_choice)]

        if result is True:
            await self.db.rpstats.update_one({"userid": ctx.author.id}, {"$set": {"win": (user["win"] + 1)}})
            await ctx.reply(content=f"You won! You had {player_c}, and I had {bot_choice}.")
        elif result is False:
            await self.db.rpstats.update_one({"userid": ctx.author.id}, {"$set": {"lost": (user["lost"] + 1)}})
            await ctx.reply(content=f"You lost. You had {player_c}, and I had {bot_choice}.")
        else:
            await self.db.rpstats.update_one({"userid": ctx.author.id}, {"$set": {"tie": (user["tie"] + 1)}})
            await ctx.reply(content=f"It's a tie! We both got {player_c}")

    @hybrid_command()
    async def rpstats(self, ctx: Context) -> None:
        """Show statistics about your rock, paper, scissors games."""
        user = await self.db.rpstats.find_one({"userid": ctx.author.id})

        if user is None:
            await self.db.rpstats.insert_one({"userid": ctx.author.id, "win": 0, "tie": 0, "lost": 0})
            # refetch the user with updated info
            user = await self.db.rpstats.find_one({"userid": ctx.author.id})

        e = Embed(title=f"{ctx.author.display_name}'s Rock, Paper, Scissors stats:", timestamp=ctx.message.created_at, color=Color.green())
        e.add_field(name="Won:", value=str(user["win"]))
        e.add_field(name="Tie:", value=str(user["tie"]))
        e.add_field(name="Lost:", value=str(user["lost"]))
        await ctx.send(embed=e)
    
    @hybrid_command(name="unoreverse")
    async def unoreverse(self, ctx: Context, *, text: str) -> None:
        """What do you think this is?"""
        reversedtxt = text[::-1]
        await ctx.send(reversedtxt)

    @hybrid_command(name="gtn", aliases=['guessthenumber'])
    async def guessthenumber(self, ctx: Context) -> None:
        """Guess a number between 1 and 10."""
        def check(m: Message) -> bool:
            """Check function for guess the number."""
            try:
                isint = int(m.content) in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            except ValueError:
                isint = False
            return bool(isint and m.author.id != ctx.bot.user.id and m.author == ctx.author)
        number = randint(0, 10)
        rnum = False
        await ctx.send("I am guessing a number between 1 and 10. You have **3** Attempts to guess it.")
        tries = 3
        while rnum is False and tries > 0:
            msg = await self.bot.wait_for('message', check=check)
            if int(msg.content) == number:
                await ctx.send(f"You guessed the right number! I was thinking of {number}")
                rnum = True
                break
            if tries == 1:
                tries -= 1
            else:
                tries -= 1
                await ctx.send(f"Wrong. You have {tries} attempt(s) left.")
        else:
            await ctx.send(f"You're out of guesses. I was thinking of the number {number}")


async def setup(bot: Client) -> None:
    """Setup Utils cog."""
    await bot.add_cog(Games(bot))
