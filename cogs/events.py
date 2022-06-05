"""Auto reporter and command logging."""
import sys
import traceback

from colorama import Back, Style
from discord import (Client, Embed, Forbidden, Guild,
                      Permissions, Webhook, AsyncWebhookAdapter)
from discord.ext.commands import (BotMissingPermissions, Cog, CommandNotFound,
                                   CommandOnCooldown, Context, DisabledCommand,
                                   MissingPermissions, MissingRequiredArgument,
                                   NoPrivateMessage, NotOwner, UserInputError)
from discord.utils import find, oauth_url


class AutoReporterEvents(Cog):
    """Auto reporter and custom events parent class."""

    __slots__ = ("bot", "webhook")

    def __init__(self, bot: Client) -> None:
        """Init Function."""
        self.bot = bot
        self.webhook = Webhook.from_url(str(bot.config["main"]["cmd_log_link"]),
                                        adapter=AsyncWebhookAdapter(bot.session)
                                        )

    @Cog.listener()
    async def on_ready(self) -> None:
        """Called when cog is loaded and ready."""
        print(Back.GREEN + Style.BRIGHT + "Events/Auto Reporter Cog loaded." + Style.RESET_ALL)

    @Cog.listener()
    async def on_command(self, ctx: Context) -> None:
        """Log when a command is called for debug purposes later."""
        em = Embed(title="Command Execution Called:", timestamp=ctx.message.created_at)
        em.set_footer(text=f"Called by {ctx.author.name}.", icon_url=str(ctx.author.avatar_url))
        em.add_field(name="Guild:", value=str(ctx.guild))
        em.add_field(name="Command:", value=str(ctx.message.content))
        await self.webhook.send(embed=em,
                                username='Aperture Expieriments'
                                )

    @Cog.listener()
    async def on_command_error(self, ctx: Context, exc: Exception) -> None:
        """Filter errors before calling the auto report job."""
        if isinstance(exc, CommandOnCooldown):
            pass
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
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'You need the **{}** permission(s) to use the {} command.'.format(fmt, ctx.command.qualified_name)
            await ctx.send(_message)
        elif isinstance(exc, BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in exc.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run the {} command.'.format(fmt, ctx.command.qualified_name)
            await ctx.send(_message)
        elif ctx.command and ctx.command.has_error_handler():
            pass
        else:
            self.bot.dispatch("auto_report", ctx, exc)

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        """Call when the bot joins a guild."""
        system_channel = guild.system_channel
        offtopic = find(lambda x: x.name == "offtopic", guild.text_channels)
        general = find(lambda x: x.name == "general", guild.text_channels)

        em = Embed(title="Thanks for adding me!",
                   description="My defalt prefix is `.`, but that can be changed with the command `changeprefix` (see `.help changeprefix` for more info). The help command is `.help`.",
                   timestamp=guild.me.joined_at,
                   color=0x36393E)
        em.add_field(name="Did i send this message in the wrong channel?",
                     value=":flushed: I try my best to find a bot channel (then find a offtopic channel, and only falling back to a random channel when I cant find any channel I can talk in.), but im not perfect.")
        em.add_field(name="Some important links:",
                     value=f"""[Support Server](https://discord.gg/S55S9J4Y3p) for when you have some bug you want to report or just want to hang out with the developer :)\
                             \n[Invite link]({oauth_url(735894171071545484, permissions=Permissions(permissions=3453353158), scopes=('bot', 'applications.commands'))}) Have someone else invite me to there server."""
                     )
        if offtopic and offtopic.permissions_for(guild.me).send_messages:
            await offtopic.send(embed=em)
        elif general and offtopic is None and general.permissions_for(guild.me).send_messages:
            await general.send(embed=em)
        elif system_channel and offtopic is None and general is None and system_channel.permissions_for(guild.me).send_messages:
            await system_channel.send(embed=em)
        else:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(embed=em)
                    break

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


def setup(bot: Client) -> None:
    """Setup function."""
    bot.add_cog(AutoReporterEvents(bot))
