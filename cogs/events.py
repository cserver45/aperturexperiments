"""Auto reporter and command logging."""
import sys
import traceback

from discord import Client, Embed, Forbidden
from discord.ext.commands import (BotMissingPermissions, Cog, CommandNotFound,
                                   CommandOnCooldown, Context, DisabledCommand,
                                   MissingPermissions, MissingRequiredArgument,
                                   NoPrivateMessage, NotOwner, UserInputError)


class AutoReporterEvents(Cog):
    """Auto reporter and custom events parent class."""

    __slots__ = ("bot")

    def __init__(self, bot: Client) -> None:
        """Init Function."""
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx: Context, exc: Exception) -> None:
        """Filter errors before calling the auto report job."""
        if isinstance(exc, CommandOnCooldown):
            await ctx.send(f"{ctx.command.name} is on cooldown. You can use it again in {round(exc.retry_after)} seconds.")
        elif isinstance(exc, CommandNotFound):
            pass
        elif isinstance(exc, DisabledCommand):
            await ctx.send("That command is disabled.")
        elif isinstance(exc, NotOwner):
            await ctx.send("Only cserver#3402 can run this becuase you cant. (and becuase there cool.)")
        elif isinstance(exc, MissingRequiredArgument):
            synta = self.bot.syntax(ctx.command)
            em = Embed(title="oops, something went wrong.", description=f"You gave {ctx.command.name} too little arguments.\nHere is the syntax for {ctx.command.qualified_name}: {synta}", timestamp=ctx.message.created_at)
            await ctx.send(embed=em)
        elif isinstance(exc, UserInputError):
            await self.bot.send_syntax_help(ctx)
        elif isinstance(exc, NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except Forbidden:
                pass
        elif isinstance(exc, MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in exc.missing_perms]
            if len(missing) > 2:
                fmt = f'{"**, **".join(missing[:-1])}, and {missing[-1]}'
            else:
                fmt = ' and '.join(missing)
            _message = f'You need the **{fmt}** permission(s) to use the {ctx.command.qualified_name} command.'
            await ctx.send(_message)
        elif isinstance(exc, BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in exc.missing_perms]
            if len(missing) > 2:
                fmt = f'{"**, **".join(missing[:-1])}, and {missing[-1]}'
            else:
                fmt = ' and '.join(missing)
            _message = f'I need the **{fmt}** permission(s) to run the {ctx.command.qualified_name} command.'
            await ctx.send(_message)
        elif ctx.command and ctx.command.has_error_handler():
            pass
        else:
            self.bot.dispatch("auto_report", ctx, exc)

    @Cog.listener()
    async def on_auto_report(self, ctx: Context, exc: Exception) -> None:
        """Auto reporter event."""
        em = Embed(title="**Oh no, my author messed up again.**",
                    description="This has been reported the error log.",
                    timestamp=ctx.message.created_at)
        em.set_footer(text="Hopefully it will be fixed soon.")

        await ctx.send(embed=em)
        channel = self.bot.get_channel(842191829910683680)
        trace = "".join(traceback.format_exception(None, exc, exc.__traceback__))
        print("\n\n\n", file=sys.stderr)
        print(trace, file=sys.stderr)
        await channel.send(f"Error report: ```{trace}\n\nSpecific Error:\n{exc}```")


async def setup(bot: Client) -> None:
    """Setup function."""
    await bot.add_cog(AutoReporterEvents(bot))
