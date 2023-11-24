"""Tasks cog."""
from itertools import cycle

from discord import Activity, Client, ActivityType
from discord.ext import tasks
from discord.ext.commands import Cog


class TasksCog(Cog):
    """Parent class."""

    __slots__ = ("bot", "db", "status")

    def __init__(self, bot: Client):
        """Init Function."""
        self.bot = bot
        self.db = bot.db
        self.status = cycle(['old blurple > new blurple',
                             'moderation bot things',
                             'Pong!',
                             'who to ban next...',
                             ' who is spamming',
                             'numbers',
                             'fire',
                             'code',
                             'the ban hammer',
                             'not another general purpose discord bot'
                             ])

    @Cog.listener()
    async def on_ready(self) -> None:
        """Called when this cog is ready."""
        self.change_status.start()


    @tasks.loop(seconds=60)
    async def change_status(self) -> None:
        """Changes the bot status in discord."""
        await self.bot.change_presence(activity=Activity(type=ActivityType.watching, name=(next(self.status))))


async def setup(bot: Client) -> None:
    """Setup the cog."""
    await bot.add_cog(TasksCog(bot))
