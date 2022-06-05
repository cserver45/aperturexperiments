"""Animals Cog."""
import orjson
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
            dogresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Dog photo link: {dogresult["url"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def cat(self, ctx: Context) -> None:
        """Get a random cat photo/gif."""
        async with self.session.get('https://aws.random.cat/meow') as resp:
            catresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Cat Photo link: {catresult["file"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def fox(self, ctx: Context) -> None:
        """Get a random fox photo/gif."""
        async with self.session.get('https://randomfox.ca/floof/') as resp:
            foxresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Fox Photo link: {foxresult["image"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def shiba(self, ctx: Context) -> None:
        """Get a random shiba photo/gif."""
        async with self.session.get('https://shibe.online/api/shibes') as resp:
            shibaresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Shiba Photo link: {shibaresult[0]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def duck(self, ctx: Context) -> None:
        """Get a random duck photo/gif."""
        async with self.session.get('https://random-d.uk/api/v2/random') as resp:
            duckresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Duck photo link: {duckresult["url"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def bird(self, ctx: Context) -> None:
        """Get a random bird photo/gif."""
        async with self.session.get('https://some-random-api.ml/img/birb') as resp:
            birdresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Bird Photo link: {birdresult["link"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def kangaroo(self, ctx: Context) -> None:
        """Get a random kangaroo photo/gif."""
        async with self.session.get('https://some-random-api.ml/img/kangaroo') as resp:
            kresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Kangaroo Photo link: {kresult["link"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def koala(self, ctx: Context) -> None:
        """Get a random koala photo/gif."""
        async with self.session.get('https://some-random-api.ml/img/koala') as resp:
            koresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Koala Photo link: {koresult["link"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def red_panda(self, ctx: Context) -> None:
        """Get a random red panda photo/gif."""
        async with self.session.get('https://some-random-api.ml/img/red_panda') as resp:
            rresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Red panda Photo link: {rresult["link"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def panda(self, ctx: Context) -> None:
        """Get a random panda photo/gif."""
        async with self.session.get('https://some-random-api.ml/img/panda') as resp:
            presult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Panda Photo link: {presult["link"]}')

    @cooldown(1, 5, BucketType.user)
    @command()
    async def whale(self, ctx: Context) -> None:
        """Get a random whale photo/gif."""
        async with self.session.get('https://some-random-api.ml/img/whale') as resp:
            wresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Whale Photo link: {wresult["link"]}')

    @cooldown(1, 5, BucketType.user)
    @command(hidden=True)
    async def lizard(self, ctx: Context) -> None:
        """Get a random lizard photo/gif.

        this is an undocumented endpoint for this api,
        so this command could fail at any time.
        """
        async with self.session.get('https://nekos.life/api/v2/img/lizard') as resp:
            lresult = await resp.json(loads=orjson.loads)
        await ctx.send(f'Lizard photo link: {lresult["url"]}')


def setup(bot: Client) -> None:
    """The setup function for animal cog."""
    bot.add_cog(Animals(bot))
