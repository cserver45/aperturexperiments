"""Animals Cog."""
from colorama import Back, Style
from discord import Client
from discord.ext.commands import BucketType, Cog, Context, command, cooldown


class Animals(Cog):
    """Animals Cog parent class."""

    __slots__ = ("bot", "session")

    def __init__(self, bot: Client) -> None:
        """Init statement."""
        self.bot = bot
        self.session = bot.session

    @Cog.listener()
    @staticmethod
    async def on_ready() -> None:
        """Call when cog is loaded and ready."""
        print(Back.GREEN + Style.BRIGHT + "Animal Cog loaded." + Style.RESET_ALL)

    @cooldown(1, 5, BucketType.user)
    @command()
    async def dog(self, ctx: Context) -> None:
        """Get a random dog photo/gif."""
        async with self.session.get('https://random.dog/woof.json') as resp:
            dogresult = await resp.json()
        await ctx.send(f'Dog photo link: {dogresult["url"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def fox(self, ctx: Context) -> None:
        """Get a random fox photo/gif."""
        async with self.session.get('https://randomfox.ca/floof/') as resp:
            foxresult = await resp.json()
        await ctx.send(f'Fox Photo link: {foxresult["image"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def shiba(self, ctx: Context) -> None:
        """Get a random shiba photo/gif."""
        async with self.session.get('https://shibe.online/api/shibes') as resp:
            shibaresult = await resp.json()
        await ctx.send(f'Shiba Photo link: {shibaresult[0]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def duck(self, ctx: Context) -> None:
        """Get a random duck photo/gif."""
        async with self.session.get('https://random-d.uk/api/v2/random') as resp:
            duckresult = await resp.json()
        await ctx.send(f'Duck photo link: {duckresult["url"]}')


async def setup(bot: Client) -> None:
    """The setup function for animal cog."""
    await bot.add_cog(Animals(bot))
