"""Tasks cog."""
from itertools import cycle

from colorama import Back, Style
from discord import Activity, Client
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
                             'moderation Bot things',
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
        if not self.bot.on_ready_mode:
            print(Back.GREEN + Style.BRIGHT + "Tasks Cog Loaded." + Style.RESET_ALL)

            # the start() methould is created at runtime (this is to shutup pylint)
            # pylint: disable=E1101

            self.change_status.start()

            # pylint: enable=E1101
        else:
            pass

    @tasks.loop(seconds=60)
    async def change_status(self) -> None:
        """Changes the bot status in discord."""
        await self.bot.change_presence(activity=Activity(type=0, name=(next(self.status))))


def setup(bot: Client) -> None:
    """Setup the cog."""
    bot.add_cog(TasksCog(bot))
