"""Utils Cog."""
import os
from datetime import timedelta
from platform import python_version
from time import time
from typing import Optional

import aiofiles
import humanize  # pylint: disable=E0401
from colorama import Back, Style
from discord import Client, DMChannel, Embed, Guild, Message, Permissions
from discord import __version__ as discord__version
from discord.errors import HTTPException
from discord.ext import commands
from discord.ext.commands import (Cog, Context, ExtensionNotFound,
                                   ExtensionNotLoaded, check_any, command,
                                   guild_only)
from discord.utils import oauth_url
from psutil import Process

# discord.py commands must have self included, even if its not used
# pylint: disable=R0201


def check_if_it_is_me() -> commands.check:
    """Check if its me (cserver)."""
    def predicate(ctx: Context) -> bool:
        return bool(ctx.message.author.id == 551448780784795651)
    return commands.check(predicate)


class UtilsA(Cog, name="Utils"):  # type: ignore[call-arg]
    """Utils Commands Parent Cog."""

    __slots__ = ("bot", "commands", "bot_version", "db")

    def __init__(self, bot: Client):
        """Init function."""
        self.bot = bot
        self.bot.remove_command("help")
        self.commands: dict = {}
        self.bot_version = str(self.bot.config["main"]["version"])
        self.db = bot.db

    @staticmethod
    @Cog.listener()
    async def on_ready() -> None:
        """Called when Utils Cog is loaded."""
        print(Back.GREEN + Style.BRIGHT + "Utils Cog Loaded." + Style.RESET_ALL)

    @Cog.listener()
    async def on_command(self, ctx: Context) -> None:
        """Call when a command is runned."""
        if ctx.message.author.bot is False:
            command_ = str(ctx.command)
            if command_ != "None":
                if command not in self.commands:
                    self.commands[command] = {"count": 1, "error": 0}
                    return
                self.commands[command]["count"] += 1

    @command(hidden=True)
    @commands.is_owner()
    async def see_servers(self, ctx: Context) -> None:
        """Placeholder."""
        for guild in self.bot.guilds:
            await ctx.send(guild.name)

    @command(hidden=True)
    @commands.is_owner()
    async def load_cog(self, ctx: Context, ext: str) -> None:
        """Load a Cog."""
        self.bot.load_extension(f'cogs.{ext}')
        await ctx.send(f"loaded {ext}.")

    @command(hidden=True)
    @commands.is_owner()
    async def unload_cog(self, ctx: Context, ext: str) -> None:
        """Unloads a Cog."""
        self.bot.unload_extension(f'cogs.{ext}')
        await ctx.send(f"unloaded {ext}.")

    @command(hidden=True)
    @commands.is_owner()
    async def reload_cog(self, ctx: Context, ext: str) -> None:
        """Reload a Cog."""
        if ext in ("-", "", " "):
            msg = ""
            for cog in os.listdir("./cogs"):
                try:
                    if cog[:-3].lower() == "jishaku":
                        continue

                    self.bot.unload_extension(f"cogs.{cog[:-3].lower()}")
                    self.bot.load_extension(f"cogs.{cog[:-3].lower()}")
                    msg += f"reloaded {cog[:-3].lower()}.\n"
                except ExtensionNotLoaded:
                    try:
                        self.bot.load_extension(f"cogs.{cog[:-3].lower}")
                        msg += f"Loaded {cog[:-3].lower()}.\n"
                    except ExtensionNotFound:
                        continue

            await ctx.send(msg)

        else:
            try:
                self.bot.reload_extension(f'cogs.{ext}')
                await ctx.send(f"reloaded {ext}.")
            except ExtensionNotLoaded:
                await ctx.send(f"I can't find {ext}.")

    @command(hidden=True)
    @commands.is_owner()
    async def toggle(self, ctx: Context, *, command_str: str) -> None:
        """Toggle an command to be disable or enabled. Can only be used by cserver#3402."""
        cmd = self.bot.get_command(command_str)

        if cmd is None:
            await ctx.send("I could not find that command to disable. Please check your spelling or view the help command.")
            return

        elif cmd == ctx.command:
            await ctx.send("You can't disable this command.")
            return

        cmd.enabled = not cmd.enabled
        await ctx.send(f"I have {'enabled' if cmd.enabled else 'disabled'} {cmd.qualified_name} for you.")

    @command(aliases=['pingt'])
    async def ping(self, ctx: Context) -> None:
        """Get ping time to websocket @ discord."""
        await ctx.send(f'Ping time: {round(self.bot.latency * 1000)}ms')

    @command(name="privacy", aliases=["privacy-policy"])
    async def get_privacy_policy(self, ctx: Context) -> None:
        """Shows the privacy policy for the bot."""
        async with aiofiles.open(r"legal/Privacy Policy", mode="r") as f:
            text = await f.read()
            await ctx.send(text)

    @command(name="bot_status", aliases=["status", "stats", "bot_info"])
    async def show_bot_status(self, ctx: Context) -> None:
        """Gets some info about the bot."""
        try:
            em = Embed(title="Bot info", colour=ctx.author.color,
                       thumbnail=self.bot.user.avatar.url,
                       timestamp=ctx.message.created_at)
        except AttributeError:
            em = Embed(title="Bot info", colour=ctx.author.color,
                       timestamp=ctx.message.created_at)

        p = Process()

        with p.oneshot():
            uptime = timedelta(seconds=time() - p.create_time())
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            pname = p.name()
            pid = p.pid
            thread_count = p.num_threads()
            mem = p.memory_full_info()

        startm = time()
        await self.db.command('ping')
        endm = time()
        mongodb_ping = f"{(endm-startm)*1000:,.0f}"

        cog_amount = 1
        for f in os.listdir("./cogs"):
            if f.endswith('.py'):
                cog_amount += 1

        actual_members_total = self.bot.total_member_count

        rnd_trp = "Wait for me to edit my message."
        fields = [
            (":writing_hand: Author:", "cserver#3402", True),
            (":robot: Bot version:", self.bot_version, True),
            ("Python info:", f"Version: `{python_version()}`,\nPid: `{pid}`,\nProcess name: `{pname}` with {thread_count} threads.", True),
            ("discord.py version:", discord__version, True),
            ("Memory used by this process:", humanize.naturalsize(mem.uss), True),
            (":adult: Users:", f"{actual_members_total[0]:,}", True),
            (":homes: Servers (guilds):", f"{actual_members_total[1]:,}", True),
            (":gear: Cogs loaded:", f"{self.bot.cog_count}/{cog_amount} loaded", True),
            (":desktop: Commmand count:", f"{self.bot.command_count} commands\nCommands runned from startup: {self.commands[command]['count']}", True),
            (":ping_pong: Ping:", f"Websocket: {round(self.bot.latency * 1000)} ms.\nRoundtrip: {rnd_trp} ms.\nMonogdb ping: {mongodb_ping} ms.", False),
            (":clock1: Uptime:", f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds", False)
        ]

        for name, value, inline in fields:
            em.add_field(name=name, value=value, inline=inline)

        start = time()
        msg = await ctx.send(embed=em)
        end = time()
        em.remove_field(9)
        rnd_trp = f"{(end-start)*1000:,.0f}"
        em.insert_field_at(index=9, name=":ping_pong: Ping:", value=f"Websocket: {round(self.bot.latency * 1000)} ms.\nRoundtrip: {rnd_trp} ms.\nMonogdb ping: {mongodb_ping} ms.", inline=False)
        await msg.edit(embed=em)

    @command()
    async def changelog(self, ctx: Context) -> None:
        """Shows the changelog if I decide to list anything new there."""
        async with aiofiles.open("CHANGELOG", mode="r") as f:
            change = await f.read()
            split_change = change.split("$$")

            for i in split_change:
                await ctx.send(i)

    # Help commands stuff after this

    @command(name="invites", hidden=True)
    async def show_invites(self, ctx: Context) -> None:
        """Shows invite links for this bot."""
        em = Embed(timestamp=ctx.message.created_at)
        em.add_field(name="Invites:", value=f"Will put other invite links here after bot gets out of open beta.\nBut here's the [direct invite link.]({oauth_url(735894171071545484, permissions=Permissions(permissions=3453353158), scopes=('bot', 'applications.commands'))})")

    async def _is_cmd_or_cog(self, ctx: Context, cogorcmd: str) -> None:
        """Sees if its a command or a cog."""
        if cogorcmd == "syntax":
            await self._syntax_help(ctx)
        elif(command_s := self.bot.get_command(cogorcmd)):
            await self._cmd_help(ctx, command_s)
        elif(cog_s := self.bot.get_cog(cogorcmd.capitalize())):
            await self._cog_help(ctx, cog_s)
        else:
            await ctx.send("That help page does not exist.")

    async def _cmd_help(self, ctx: Context, command_s: command) -> None:
        """Helper function for cmd help page."""
        if command_s.enabled is False:
            await ctx.send(f"{command_s.qualified_name} has been disabled.")
            return
        em = Embed(title=f"Help with `{command_s}`.",
                    description=self.bot.syntax(command_s),
                    colour=ctx.author.colour,
                    timestamp=ctx.message.created_at)
        try:
            cooldown_time = str(command_s.buckets.cooldown.per)
        except AttributeError:
            cooldown_time = "0"

        try:
            em.add_field(name="Command Description:", value=command_s.help)
            em.add_field(name="Cooldown Time:", value=f"{cooldown_time} seconds.")
            em.add_field(name="Catergory:", value=command_s.cog_name)
        except HTTPException:
            em.add_field(name="Command Description:", value="None")
            em.add_field(name="Cooldown Time:", value=f"{cooldown_time} seconds.")
            em.add_field(name="Catergory:", value=command_s.cog_name)
        await ctx.send(embed=em)

    async def _cog_help(self, ctx: Context, cog_s: Cog) -> None:
        """Helper function for catergory help page."""
        cm = cog_s.get_commands()
        cmdl = []
        cmd_str = str()
        for cmds in cm:
            if cmds.hidden is True:
                continue
            elif cmds.enabled is False:
                continue
            else:
                cmdl.append(cmds.name)

        cmdl.sort()
        for cmdlo in cmdl:
            other_info = self.bot.get_command(cmdlo)
            cmd_str = cmd_str + f"{cmdlo}:  {other_info.short_doc}\n"
        em = Embed(title=f"{cog_s.qualified_name} Catergory Commands.", description=str(cmd_str))
        await ctx.send(embed=em)

    async def _main_help(self, ctx: Context) -> None:
        """If no command is given, this is what is given."""
        em = Embed(title="Aperture Expieriments Help Page",
                    description=f"Use **`help [command]`** for more info on a command\nYou can also do **`help [catergory]`** for help on a catergory.\nIf you have a problem, you could also join the [support server](https://discord.gg/HZmgbyKejA) to tell us about it.\n**To see what the syntax means, do `help syntax`**",
                    colour=ctx.author.colour,
                    timestamp=ctx.message.created_at)
        cogs = [c for c in self.bot.cogs]  # pylint: disable=R1721
        cogs.sort()
        for cog in cogs:
            cogi = self.bot.get_cog(cog)
            cm = cogi.get_commands()
            cmdl = []
            cmd_str = str()
            for cmds in cm:
                if cmds.hidden is True:
                    continue
                elif cmds.enabled is False:
                    continue
                else:
                    cmdl.append(cmds.name)

            if not cmdl:
                continue
            else:
                cmdl.sort()
                for cmdlo in cmdl:
                    cmd_str = cmd_str + f"{cmdlo}  "
                em.add_field(name=f"__{cog}__", value=f"{str(cmd_str)}", inline=False)
        await ctx.send(embed=em)

    async def _syntax_help(self, ctx: Context) -> None:
        """Show info about what the syntax means."""
        em = Embed(title="What means what.", timestamp=ctx.message.created_at,
                   description="""`|` is to show aliases/other ways to say a command.
                                  `[]` is for optional arguments.
                                  `<>` is for requred arguments.""")
        await ctx.send(embed=em)

    async def prefix_help_page(self, ctx: Context) -> None:
        """Show info about what your prefix is (mostly useless)."""

    @commands.cooldown(1, 5, commands.BucketType.user)
    @command(name="help", aliases=["info"])
    async def show_help(self, ctx: Context, cmd: Optional[str]) -> None:
        """Shows this message."""
        if cmd is None:
            await self._main_help(ctx)
        else:
            await self._is_cmd_or_cog(ctx, cmd)


def setup(bot: Client) -> None:
    """Setup Utils cog."""
    bot.add_cog(UtilsA(bot))
