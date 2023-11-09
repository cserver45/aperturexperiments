"""Moderation Cog."""
from typing import Optional

from colorama import Back, Style
from discord import Client, Embed
from discord.errors import Forbidden
from discord.ext import commands
from discord.ext.commands import Cog, Context, Greedy, MemberConverter, command

from .lib.converters import BannedUser  # pylint: disable=E0402

# discord.py commands must have self included, even if its not used
# pylint: disable=R0201


class Moderation(Cog):
    """Moderation Cog Parent class."""

    __slots__ = ("bot",)

    def __init__(self, bot: Client) -> None:
        """Init function."""
        self.bot = bot

    @staticmethod
    @Cog.listener()
    async def on_ready() -> None:
        """Called when this cog is ready."""
        print(Back.GREEN + Style.BRIGHT + "Moderation Cog Loaded." + Style.RESET_ALL)

    @command()
    @commands.bot_has_permissions(send_messages=True, manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: Context, amount: int = 5) -> Context:
        """Clear `x` ammount of messages."""
        if amount < 0:
            return await ctx.send("You can't specify a negitive number of messages to delete.")
        try:
            await ctx.message.delete()
            try:
                await ctx.channel.purge(limit=int(amount))
                await ctx.send(f":+1: I have deleted {amount + 1} message(s).", delete_after=5)
            except (TypeError, ValueError):
                await ctx.send("That is invalid input. Specify a number.")
        except Forbidden:
            return await ctx.send("I don't have the permission to clear messages (manage messages.)")

    @command()
    @commands.bot_has_permissions(send_messages=True, kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: Context, members: Greedy[MemberConverter] = None, *, reason: Optional[str] = None) -> None:
        """Kick a member from the Discord Server."""
        if not members:
            await ctx.send('Please mention a member')
            return
        for mem in members:
            try:
                await mem.kick(reason=reason)
                await ctx.send(f'{mem.display_name} was kicked from the server')
            except Forbidden:
                await ctx.send("The Aperture Expieriments role is below what that users highest role is. Fix your roles by putting my role above there's.")

    @command()
    @commands.bot_has_permissions(send_messages=True, ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: Context, members: Greedy[MemberConverter] = None, *, reason: Optional[str] = "No reason was given.") -> None:
        """Bans a member from the Discord Server."""
        if not members:
            await ctx.send('Please mention a member')
            return
        for mem in members:
            try:
                await mem.ban(reason=reason)
                await ctx.send(f'{mem.display_name} was banned from the server')
            except Forbidden:
                await ctx.send("The Aperture Expieriments role is below what that users highest role is. Fix your roles by putting my role above there's.")

    @command()
    @commands.bot_has_permissions(send_messages=True, ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: Context, members: Greedy[BannedUser], reason: Optional[str] = "No reason was given.") -> None:
        """Unban a user that was banned from the server. Does not take mentions, only id's and usernames with descriminators."""
        # thanks Parafoxia for this code sniplet
        if not members:
            await ctx.send(":negative_squared_cross_mark: No valid members were passed.")
        else:
            count = 0

            async with ctx.typing():
                for member in members:
                    await ctx.guild.unban(member, reason=reason)
                    count += 1

                if count > 0:
                    await ctx.send(f":white_check_mark: {count:,} user(s) were unbanned.")
                else:
                    await ctx.send(":negative_squared_cross_mark: No users were unbanned.")

    @command(aliases=["setnick"])
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(send_messages=True, manage_nicknames=True)
    async def set_nickname(self, ctx: Context, member: MemberConverter, *, nickname: str) -> None:
        """Change a member's nickname."""
        member = member or ctx.author

        if len(nickname) > 32:
            await ctx.send("Nicknames can not be more than 32 characters in length.")
        else:
            try:
                await member.edit(nick=nickname)
                await ctx.send("That member's nickname has been changed.")
            except Forbidden:
                await ctx.send(f"I am below the highest role that {member.display_name} has.")

    @command(aliases=['whoami', 'userinfo'])
    async def whois(self, ctx: Context, member: MemberConverter = None) -> None:
        """See who a user is (account date creation, joined server date, etc)."""
        if member is None:
            member = ctx.author

        roles = [role.mention for role in member.roles[1:]]  # otherwhise it would be @@everyone
        roles.append('@everyone')  # adds @everyone back to the list

        Em = Embed(title=f'Info on {member}', timestamp=ctx.message.created_at)
        Em.set_thumbnail(url=member.avatar_url)
        Em.set_footer(text=f"Requested by {ctx.author}.")
        Em.add_field(name="ID:", value=member.id)
        Em.add_field(name="Display Name:", value=member.display_name)
        Em.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        Em.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        Em.add_field(name="Roles:", value="".join(role for role in roles))
        Em.add_field(name="Highest Role:", value=member.top_role)
        Em.add_field(name='Avatar:', value=f'[Link to avatar]({member.avatar_url})')

        await ctx.send(embed=Em)


async def setup(bot: Client) -> None:
    """Setup the cog."""
    await bot.add_cog(Moderation(bot))
