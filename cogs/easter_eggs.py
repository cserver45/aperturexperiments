"""Easter eggs Cog. Shhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh..."""
from colorama import Back, Style
from discord import Client, Colour, Embed, Message, NotFound
from discord.ext.commands import Cog, Context, command

# discord.py commands must have self included, even if its not used
# pylint: disable=R0201


class EasterEggs(Cog):
    """Easter egg parent class."""

    __slots__ = ("bot",)

    def __init__(self, bot: Client) -> None:
        """Init function."""
        self.bot = bot

    @Cog.listener()
    @staticmethod
    async def on_ready() -> None:
        """Call when the Cog is loaded."""
        print(Back.GREEN + Style.BRIGHT + "Easter Eggs loaded. Shhhhhhhhhhhhh..." + Style.RESET_ALL)

    @Cog.listener()
    @staticmethod
    async def on_message(msg: Message) -> None:
        """Call when a message is sent."""
        if msg.author.bot:
            return
        if "chat dead" in msg.content or "dead chat" in msg.content:
            await msg.channel.send("Well, its not **acutaly** dead because you just send a message here, and I happen to be listening to this channel at the same time.")

    @command()
    async def beep(self, ctx: Context) -> None:
        """Beep boop boop beep?"""
        beepembed = Embed(title='beep boop boop beep?', colour=Colour.red(),
                          timestamp=ctx.message.created_at)
        beepembed.set_footer(text='You found an easter egg :)')
        await ctx.send(embed=beepembed)

    @command()
    async def robot(self, ctx: Context) -> None:
        """Why do you think im a robot?"""
        robotembed = Embed(title='but i\'m not a robot!', colour=Colour.green(),
                            timestamp=ctx.message.created_at)
        robotembed.set_footer(text='You found an easter egg :)')
        await ctx.send(embed=robotembed)

    @command()
    async def pingtime(self, ctx: Context) -> None:
        """Ping!"""
        pingembed = Embed(title='Ping!', colour=Colour.blue(), timestamp=ctx.message.created_at)
        pingembed.set_footer(text='You found an easter egg :)')
        await ctx.send(embed=pingembed)

    @command()
    async def rgb(self, ctx: Context) -> None:
        """No, this is not what you think this is."""
        rgbembed = Embed(title='Wow you actualy pay attention at the embed color\'s',
                         colour=Colour.orange(),
                         timestamp=ctx.message.created_at)
        rgbembed.set_footer(text='You found a more hidden easter egg >:)')
        await ctx.send(embed=rgbembed)

    @command()
    async def onfire(self, ctx: Context) -> None:
        """:fire: :fire: :fire: :fire: :fire: :fire: :fire:..."""
        await ctx.send(':fire: :fire: :fire: :fire: :fire: :fire: :fire:')

    @command()
    async def nitro(self, ctx: Context) -> None:
        """100% legit free nitro right?"""
        try:
            await ctx.message.delete()
        except NotFound:
            pass

        await ctx.send('https://tenor.com/view/rick-roll-deal-with-it-rick-astley-never-gonna-give-you-up-gif-14204545')

    @command()
    async def unoreverse(self, ctx: Context, *, text: str) -> None:
        """What do you think this is?"""
        reversedtxt = text[::-1]
        await ctx.send(reversedtxt)


def setup(bot: Client) -> None:
    """Setup easter egg cog."""
    bot.add_cog(EasterEggs(bot))
