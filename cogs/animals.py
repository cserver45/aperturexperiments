"""Animals Cog."""
from discord import Client, Embed
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
        result = await resp.json()
        em = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
        em.set_image(url=result["url"])
        await ctx.send(embed=em)

    @cooldown(1, 5, BucketType.user)
    @hybrid_command()
    async def fox(self, ctx: Context) -> None:
        """Get a random fox photo/gif."""
        resp = await self.session.get('https://randomfox.ca/floof/')
        result = await resp.json()
        em = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
        em.set_image(url=result["image"])
        await ctx.send(embed=em)

    @cooldown(1, 5, BucketType.user)
    @hybrid_command()
    async def shiba(self, ctx: Context) -> None:
        """Get a random shiba photo/gif."""
        resp = await self.session.get('https://shibe.online/api/shibes')
        result = await resp.json()
        em = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
        em.set_image(url=result[0])
        await ctx.send(embed=em)

    @cooldown(1, 5, BucketType.user)
    @hybrid_command()
    async def duck(self, ctx: Context) -> None:
        """Get a random duck photo/gif."""
        resp = await self.session.get('https://random-d.uk/api/v2/random')
        result = await resp.json()
        em = Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
        em.set_image(url=result["url"])
        await ctx.send(embed=em)


async def setup(bot: Client) -> None:
    """The setup function for animal cog."""
    await bot.add_cog(Animals(bot))
