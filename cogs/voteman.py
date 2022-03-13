"""Cog that manages the bot lists."""
import aiohttp
from colorama import Back, Style
from discord import Client
from discord.ext import tasks
from discord.ext.commands import Cog


class VoteMan(Cog):
    """Parent class."""

    TOPGGURI = "https://top.gg/api"
    FATESLISTURI = "https://fateslist.xyz/api/v2"
    BOTID = "735894171071545484"

    def __init__(self, bot: Client):
        """Init Function."""
        self.bot = bot
        self.db = bot.db
        self.session = bot.session
        self.webhook = bot.webhook

    @Cog.listener()
    async def on_ready(self) -> None:
        """Called when this cog is ready."""
        if not self.bot.on_ready_mode or self.on_ready_overide:
            print(Back.GREEN + Style.BRIGHT + "Vote Manager Cog Loaded." + Style.RESET_ALL)
            # the start() methould is created at runtime (this is to shutup pylint)
            # pylint: disable=E1101

            if self.bot.argus.token == "protoken":
                self.update_topgg_list_data.start()
            # pylint: enable=E1101
        else:
            pass

    @tasks.loop(minutes=30)
    async def update_topgg_list_data(self) -> None:
        """Update the data on top.gg every 30 minutes."""
        headers = {
            "User-Agent": f"Aperture Expieriments {self.bot.config['main']['version']} using aiohttp version {aiohttp.__version__}",
            "Content-Type": "application/json",
            "Authorization": self.bot.config["topgg"]["token"],
        }

        payload = {
            "server_count": self.bot.guild_count,
            "shard_count": self.bot.shard_count
        }

        async with self.session.post(f"{self.TOPGGURI}/bots/stats", json=payload, headers=headers) as resp:
            if resp.status == 200:
                await self.webhook.send(':white_check_mark: Sucessfully Submitted Gulld and Shard Count to top.gg.', username='Aperture Expieriments Top.gg Status')
            else:
                await self.webhook.send(':negative_squared_cross_mark: Failed Submitting Gulld and Shard Count to top.gg.', username='Aperture Expieriments Top.gg Status')

    @tasks.loop(minutes=30)
    async def update_fateslist_data(self) -> None:
        """Update the data on fateslist every 30 minutes."""
        headers = {
            "User-Agent": f"Aperture Expieriments {self.bot.config['main']['version']} using aiohttp version {aiohttp.__version__}",
            "Content-Type": "application/json",
            "Authorization": self.bot.config["fateslist"]["token"],
        }

        members = self.bot.total_member_count

        payload = {
            "guild_count": self.bot.guild_count,
            "shard_count": self.bot.shard_count,
            "user_count": members[0],
        }

        async with self.session.post(f"{self.FATESLISTURI}/bots/{self.BOTID}/stats", json=payload, headers=headers) as resp:
            if resp.status == 200:
                await self.webhook.send(':white_check_mark: Sucessfully Submitted Gulld and Shard Count to fateslist.', username='Aperture Expieriments fateslist Status')
            else:
                await self.webhook.send(':negative_squared_cross_mark: Failed Submitting Gulld and Shard Count to fateslist.', username='Aperture Expieriments fateslist Status')
                print(await resp.text())


def setup(bot: Client) -> None:
    """Setup the cog."""
    bot.add_cog(VoteMan(bot))
