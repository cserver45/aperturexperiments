"""Animals Cog."""
from discord import Client
from discord.ext.commands import BucketType, Cog, Context, hybrid_command, cooldown


class Animals(Cog):
    """Animals Cog parent class."""

    __slots__ = ("bot", "session")

    def __init__(self, bot: Client) -> None:
        """Init statement."""
        self.bot = bot
        self.session = bot.session

    @cooldown(1, 5, BucketType.user)
    @hybrid_command()
    async def dog(self, ctx: Context) -> None:
        """Get a random dog photo/gif."""
        resp = await self.session.get('https://random.dog/woof.json')
        dogresult = await resp.json()
        await ctx.send(f'Dog photo link: {dogresult["url"]}')

    @cooldown(1, 5, BucketType.user)
    @hybrid_command()
    async def fox(self, ctx: Context) -> None:
        """Get a random fox photo/gif."""
        resp = await self.session.get('https://randomfox.ca/floof/')
        foxresult = await resp.json()
        await ctx.send(f'Fox Photo link: {foxresult["image"]}')

    @cooldown(1, 5, BucketType.user)
    @hybrid_command()
    async def shiba(self, ctx: Context) -> None:
        """Get a random shiba photo/gif."""
        resp = await self.session.get('https://shibe.online/api/shibes')
        shibaresult = await resp.json()
        await ctx.send(f'Shiba Photo link: {shibaresult[0]}')

    @cooldown(1, 5, BucketType.user)
    @hybrid_command()
    async def duck(self, ctx: Context) -> None:
        """Get a random duck photo/gif."""
        resp = await self.session.get('https://random-d.uk/api/v2/random')
        duckresult = await resp.json()
        await ctx.send(f'Duck photo link: {duckresult["url"]}')


async def setup(bot: Client) -> None:
    """The setup function for animal cog."""
    await bot.add_cog(Animals(bot))
