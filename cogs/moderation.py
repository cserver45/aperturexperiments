"""Moderation Cog."""
from typing import Optional

from discord import Client, Embed
from discord.errors import Forbidden
from discord.ext import commands
from discord.ext.commands import Cog, Context, Greedy, MemberConverter, hybrid_command

# discord.py commands must have self included, even if its not used
# pylint: disable=R0201


class Moderation(Cog):
    """Moderation Cog Parent class."""

    __slots__ = ("bot",)

    def __init__(self, bot: Client) -> None:
        """Init function."""
        self.bot = bot

    @hybrid_command()
    @commands.bot_has_permissions(send_messages=True, manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: Context, amount: int = 5) -> Context:
        """Clear `x` ammount of messages."""
        if amount < 0:
            return await ctx.send("You can't specify a negitive number of messages to delete.")
        try:
            try:
                await ctx.send(f":+1: I have deleted {amount} message(s).")
                await ctx.channel.purge(limit=int(amount))
            except (TypeError, ValueError):
                await ctx.send("That is invalid input. Specify a number.")
        except Forbidden:
            return await ctx.send("I don't have the permission to clear messages (manage messages.)")

    @hybrid_command()
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
                await ctx.send("The Aperture Expieriments role is below what that users highest role is. Fix your roles by putting my role above theirs.")

    @hybrid_command()
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
                await ctx.send("The Aperture Expieriments role is below what that users highest role is. Fix your roles by putting my role above theirs.")

    @hybrid_command()
    @commands.bot_has_permissions(send_messages=True, ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: Context, member, reason: Optional[str] = "No reason was given.") -> None:
        """Unban a user that was banned from the server. IDs only."""
        if not member:
            await ctx.send("Please give only the IDs of the members.")
        else:

            async with ctx.typing():
                user = await self.bot.fetch_user(member)
                await ctx.guild.unban(user, reason=reason)

                await ctx.send("That person has been unbanned.")

    @hybrid_command(aliases=["setnick"])
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(send_messages=True, manage_nicknames=True)
    async def set_nickname(self, ctx: Context, member: MemberConverter, *, nickname: str) -> None:
        """Change a member's nickname."""
        member = member or ctx.author

        if len(nickname) > 32:
            await ctx.send("Nicknames can not be more than 32 characters in length.")
        else:
            try:
                updated_nick = await member.edit(nick=nickname)
                await ctx.send(f"That member's nickname has been changed to {updated_nick.nick}")
            except Forbidden:
                await ctx.send(f"I am below the highest role that {member.display_name} has.")

    @hybrid_command(aliases=['whoami', 'userinfo'])
    async def whois(self, ctx: Context, member: MemberConverter = None) -> None:
        """See who a user is (account date creation, joined server date, etc)."""
        if member is None:
            member = ctx.author

        roles = [role.mention for role in member.roles[1:]]  # otherwhise it would be @@everyone
        roles.append('@everyone')  # adds @everyone back to the list

        Em = Embed(title=f'Info on {member}', timestamp=ctx.message.created_at)
        Em.set_thumbnail(url=member.avatar.url if member.avatar is not None else None)
        Em.set_footer(text=f"Requested by {ctx.author}.")
        Em.add_field(name="ID:", value=member.id)
        Em.add_field(name="Display Name:", value=member.display_name)
        Em.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        Em.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        Em.add_field(name="Roles:", value="".join(role for role in roles))
        Em.add_field(name="Highest Role:", value=member.top_role)
        if member.avatar is not None:
            Em.set_thumbnail(url=member.avatar.url)
            Em.add_field(name='Avatar:', value=f'[Link to avatar]({member.avatar.url})')

        await ctx.send(embed=Em)


async def setup(bot: Client) -> None:
    """Setup the cog."""
    await bot.add_cog(Moderation(bot))
