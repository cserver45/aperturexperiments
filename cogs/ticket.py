"""Ticket System Cog."""
from colorama import Back, Style
from discord import Client, Embed, RawReactionActionEvent
from discord.errors import NotFound
from discord.ext.commands import Cog, Context, MemberConverter, check, command
from discord.ext.commands.errors import CheckFailure, MemberNotFound


def check_if_it_is_ticket() -> check:
    """Checks if its a ticket."""
    def predicate(ctx: Context) -> bool:
        return bool(ctx.channel.category_id == 844628558160461868)
    return check(predicate)


class TicketSystem(Cog):
    """Ticket system parent class."""

    def __init__(self, bot: Client):
        """Init function."""
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        """Called when cog is loaded and ready."""
        print(Back.GREEN + Style.BRIGHT + "Ticket System Cog loaded." + Style.RESET_ALL)
        guild = self.bot.get_guild(843208429409402920)
        channel = guild.get_channel(845059736687607878)
        msg = await channel.fetch_message(845059813062869003)
        await msg.clear_reactions()
        await msg.add_reaction("📩")

    @command()
    @check_if_it_is_ticket()
    async def add_user(self, ctx: Context, member: MemberConverter) -> None:
        """Add a user to the ticket."""
        await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
        await ctx.send(f"Added {member.mention} to the ticket.")

    @command(aliases=["delete_user"])
    @check_if_it_is_ticket()
    async def remove_user(self, ctx: Context, member: MemberConverter) -> None:
        """Remove a user from the ticket."""
        await ctx.channel.set_permissions(member, read_messages=False, send_messages=False)
        await ctx.send(f"Removed {member.display_name} from the ticket.")

    @add_user.error
    async def add_user_error(self, ctx: Context, exc: Exception) -> None:
        """Error handeler."""
        if isinstance(exc, MemberNotFound):
            await ctx.send("I could not find that member. Check your spelling.")
            return
        elif isinstance(exc, CheckFailure):
            await ctx.send("This is not a ticket you dummy.")
            return

    @remove_user.error
    async def remove_user_error(self, ctx: Context, exc: Exception) -> None:
        """Error handeler."""
        if isinstance(exc, MemberNotFound):
            await ctx.send("I could not find that member. Check your spelling.")
            return
        elif isinstance(exc, CheckFailure):
            await ctx.send("This is not a ticket you dummy.")
            return

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        """Call when a reaction event has been sent (not in cache)."""
        guild = await self.bot.fetch_guild(payload.guild_id)
        guild2 = self.bot.get_guild(843208429409402920)
        channel = guild2.get_channel(845059736687607878)
        try:
            msg = await channel.fetch_message(payload.message_id)
        except NotFound:
            return
        member = await guild.fetch_member(payload.user_id)

        if member.id == 776987330967240716 or member.id == 735894171071545484:
            return
        category = self.bot.get_channel(844628558160461868)
        if payload.emoji.name == "📩" and payload.guild_id == 843208429409402920:
            await msg.remove_reaction("📩", member)
            channel = await guild.create_text_channel(name=f'ticket-{member}', category=category, sync_permissions=True, position=0)
            await channel.set_permissions(member, read_messages=True, send_messages=True)
            em = Embed(title="Commands:")
            em.add_field(name="add_user", value="Add a user to this ticket.")
            await channel.send(f"Welcome {member.name}. Our team will respond to you as soon as possible.")
            await channel.send("Please describe your problem in detail to help speed up the process.")
            await channel.send(f'{member.mention}', delete_after=5)


def setup(bot: Client) -> None:
    """Setup function."""
    bot.add_cog(TicketSystem(bot))
