"""Custom converters used by the bot."""
import discord
from discord.ext import commands

# stupid pylint, i know that the args are diffrent.
# pylint: disable=W0221


class BannedUser(commands.Converter):
    """Checks if a user is a banned one."""

    # thanks parafoxia from the bot solaris for this converter
    async def convert(self, ctx: commands.Context, arg: str) -> discord.User:
        """Converter."""
        if ctx.guild.me.guild_permissions.ban_members:
            if arg.isdigit():
                try:
                    return (await ctx.guild.fetch_ban(discord.Object(id=int(arg)))).user
                except discord.NotFound as e:
                    raise commands.BadArgument from e

            banned = [e.user for e in await ctx.guild.bans()]
            if banned:
                if (user := discord.utils.find(lambda u: str(u) == arg, banned)) is not None:
                    return user
                else:
                    raise commands.BadArgument
