"""Member join/leave Cog."""
from colorama import Back, Style
from discord import Client
from discord.ext.commands import Cog, MemberConverter


class JoinLeave(Cog):
    """Parent class."""

    __slots__ = ('bot',)

    def __init__(self, bot: Client):
        """Init function."""
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member: MemberConverter) -> None:
        """Called when a member joins the server."""
        if member.guild.id == 843208429409402920:
            channel = self.bot.get_channel(845486634912186389)
            await channel.send(f"{member.mention} has joined us. Go look at <#843211264376176690> and <#845059150723284993> before going to <#843208429409402923>.")

    @Cog.listener()
    async def on_member_remove(self, member: MemberConverter) -> None:
        """Called when a member leaves the server."""
        if member.guild.id == 843208429409402920:
            channel = self.bot.get_channel(845486634912186389)
            await channel.send(f"{member.display_name} has left us. We now have only {len(member.guild.members)} members.")


async def setup(bot: Client) -> None:
    """Setup function."""
    await bot.add_cog(JoinLeave(bot))
