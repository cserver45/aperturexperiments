"""Image manipulation Cog."""
import asyncio
import functools
import random
from io import BytesIO
from random import randint
from typing import Optional

from colorama import Back, Style
from discord import Client, Embed, File
from discord.ext.commands import Cog, Context, MemberConverter, command
from PIL import Image, ImageDraw, ImageFont


class ImageDiscord(Cog, name="Image"):  # type: ignore[call-arg]
    """Image cog parent class."""

    def __init__(self, bot: Client):
        """Init Function."""
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        """Called when cog is loaded and ready."""
        print(Back.GREEN + Style.BRIGHT + "Image Cog loaded." + Style.RESET_ALL)

    @command()
    async def wanted(self, ctx: Context, user: Optional[MemberConverter] = None) -> None:
        """Get someone on the wanted list (not literaly)."""
        if user is None:
            user = ctx.author

        wanted = Image.open("photos/wanted.jpg")
        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((500, 500))
        wanted.paste(pfp, (454, 590))
        img = BytesIO()
        wanted.save(img, format="jpeg")
        img.seek(0)

        await ctx.send(file=File(img, "result.jpg"))

    @command()
    async def triggered(self, ctx: Context, user: Optional[MemberConverter] = None) -> None:
        """This should require no description."""
        if user is None:
            user = ctx.author

        asset = user.avatar_url_as(size=128)
        avatar = Image.open(BytesIO(await asset.read())).resize((320, 320)).convert('RGBA')
        triggered = Image.open('photos/triggered/triggered.bmp')
        tint = Image.open('photos/triggered/red.bmp').convert('RGBA')
        blank = Image.new('RGBA', (256, 256), color=(231, 19, 29))
        frames = []

        for i in range(8):
            base = blank.copy()

            if i == 0:
                base.paste(avatar, (-16, -16), avatar)
            else:
                base.paste(avatar, (-32 + randint(-16, 16), -32 + randint(-16, 16)), avatar)

            base.paste(tint, (0, 0), tint)

            if i == 0:
                base.paste(triggered, (-10, 200))
            else:
                base.paste(triggered, (-12 + randint(-8, 8), 200 + randint(0, 12)))

            frames.append(base)

        b = BytesIO()
        frames[0].save(b, save_all=True, append_images=frames[1:], format='gif', loop=0, duration=20, disposal=2,
                       optimize=True)
        b.seek(0)

        await ctx.send(file=File(b, "result.gif"))

    @command()
    async def america(self, ctx: Context, user: Optional[MemberConverter] = None) -> None:
        """None."""
        if user is None:
            user = ctx.author

        asset = user.avatar_url_as(size=128)
        imgb = BytesIO(await asset.read())

        def make_img(imgb: BytesIO) -> BytesIO:
            img1 = Image.open(imgb).convert('RGBA').resize((480, 480))
            img2 = Image.open('photos/america.gif')
            img1.putalpha(128)

            out = []
            for i in range(0, img2.n_frames):
                img2.seek(i)
                f = img2.copy().convert('RGBA').resize((480, 480))
                f.paste(img1, (0, 0), img1)
                out.append(f.resize((256, 256)))

            b = BytesIO()
            out[0].save(b, format='gif', save_all=True, append_images=out[1:], loop=0, disposal=2, optimize=True, duration=30)
            b.seek(0)
            return b

        fake_task = functools.partial(make_img, imgb)
        task = self.bot.loop.run_in_executor(None, fake_task)
        try:
            await asyncio.wait_for(task, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("It took too long to do that. Failed.")
            return
        else:
            await ctx.send(file=File(task.result(), "result.gif"))

    @command()
    async def communism(self, ctx: Context, user: Optional[MemberConverter] = None) -> None:
        """None."""
        if user is None:
            user = ctx.author

        asset = user.avatar_url_as(size=128)
        imgb = BytesIO(await asset.read())

        def make_img(imgb: BytesIO) -> BytesIO:
            img1 = Image.open(imgb).convert('RGBA').resize((300, 300))
            img2 = Image.open('photos/communism.gif')
            img1.putalpha(96)

            out = []
            for i in range(0, img2.n_frames):
                img2.seek(i)
                f = img2.copy().convert('RGBA').resize((300, 300))
                f.paste(img1, (0, 0), img1)
                out.append(f.resize((256, 256)))

            b = BytesIO()
            out[0].save(b, format='gif', save_all=True, append_images=out[1:], loop=0, disposal=2, optimize=True, duration=40)
            img2.close()
            b.seek(0)
            return b

        fake_task = functools.partial(make_img, imgb)
        task = self.bot.loop.run_in_executor(None, fake_task)
        try:
            await asyncio.wait_for(task, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("It took too long to do that. Failed.")
            return
        else:
            await ctx.send(file=File(task.result(), "result.gif"))

    @command()
    async def delete(self, ctx: Context, user: Optional[MemberConverter] = None) -> None:
        """Just try it on someone. You'll be glad with the result."""
        if user is None:
            user = ctx.author

        asset = user.avatar_url_as(size=128)
        imgb = BytesIO(await asset.read())

        def make_img(imgb: BytesIO) -> BytesIO:
            delete = Image.open("photos/delete.png")

            pfp = Image.open(imgb)
            pfp = pfp.resize((202, 202))

            delete.paste(pfp, (120, 134))
            img = BytesIO()
            delete.save(img, format="png")
            img.seek(0)
            return img

        fake_task = functools.partial(make_img, imgb)
        task = self.bot.loop.run_in_executor(None, fake_task)
        try:
            await asyncio.wait_for(task, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("It took too long to do that. Failed.")
            return
        else:
            await ctx.send(file=File(task.result(), "result.png"))

    @command()
    async def holdup(self, ctx: Context, *, text: str) -> None:
        """Wait a minute..."""

        def make_img() -> BytesIO:
            im = Image.open('photos/holdup.png')
            font = ImageFont.truetype("fonts/Roboto.ttf", 24)

            drawn = ImageDraw.Draw(im)

            drawn.text((10, 10), text, fill=(0, 0, 0), font=font)
            img = BytesIO()
            im.save(img, format="png")
            img.seek(0)
            return img

        task = self.bot.loop.run_in_executor(None, make_img)
        try:
            await asyncio.wait_for(task, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("It took too long to do that. Failed.")
            return
        else:
            await ctx.send(file=File(task.result(), "result.png"))

    @command()
    async def neverhave(self, ctx: Context, *, text: str) -> None:
        """Have you been offended but 100% agree with someone? use this."""

        def make_img() -> BytesIO:
            im = Image.open('photos/neverbefore.png')
            font = ImageFont.truetype("fonts/Roboto.ttf", 24)

            drawn = ImageDraw.Draw(im)

            drawn.text((10, 10), text, fill=(0, 0, 0), font=font)
            img = BytesIO()
            im.save(img, format="png")
            img.seek(0)
            return img

        task = self.bot.loop.run_in_executor(None, make_img)
        try:
            await asyncio.wait_for(task, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("It took too long to do that. Failed.")
            return
        else:
            await ctx.send(file=File(task.result(), "result.png"))

    @command()
    async def hackerman(self, ctx: Context, *, text: str) -> None:
        """Pro haxer man."""

        def make_img() -> BytesIO:
            im = Image.open('photos/hackerman.png')
            font = ImageFont.truetype("fonts/Roboto.ttf", 32)

            drawn = ImageDraw.Draw(im)

            drawn.text((10, 10), text, fill=(0, 0, 0), font=font)
            img = BytesIO()
            im.save(img, format="png")
            img.seek(0)
            return img

        task = self.bot.loop.run_in_executor(None, make_img)
        try:
            await asyncio.wait_for(task, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("It took too long to do that. Failed.")
            return
        else:
            await ctx.send(file=File(task.result(), "result.png"))

    @command(aliases=['michaelsoft-binbows'])
    async def msbinbows(self, ctx: Context, *, text: str) -> None:
        """Totaly isin't a ripoff."""

        def make_img() -> BytesIO:
            im = Image.open('photos/binbows.png')
            font = ImageFont.truetype("fonts/Roboto.ttf", 32)

            drawn = ImageDraw.Draw(im)

            drawn.text((10, 10), text, fill=(0, 0, 0), font=font)
            img = BytesIO()
            im.save(img, format="png")
            img.seek(0)
            return img

        task = self.bot.loop.run_in_executor(None, make_img)
        try:
            await asyncio.wait_for(task, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("It took too long to do that. Failed.")
            return
        else:
            await ctx.send(file=File(task.result(), "result.png"))

    @command()
    async def codememes(self, ctx: Context) -> None:
        """Get some memes from r/ProgrammerHumor."""
        subreddit = await self.bot.reddit.subreddit("ProgrammerHumor")
        all_subs = []
        async for submission in subreddit.hot(limit=100):
            all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        url = random_sub.url

        if random_sub.over_18:
            await ctx.send("That post from that subreddit was marked as NSFW. (in the future this will check if its an nsfw channel, and if it is, then this check will be bypassed.)")
            return

        em = Embed(title=name, timestamp=ctx.message.created_at)
        em.set_image(url=url)

        await ctx.send(embed=em)

    @command()
    async def brokestuff(self, ctx: Context) -> None:
        """Get some memes from r/SoftwareGore."""
        subreddit = await self.bot.reddit.subreddit("SoftwareGore")
        all_subs = []
        async for submission in subreddit.hot(limit=100):
            all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        url = random_sub.url

        if random_sub.over_18:
            await ctx.send("That post from that subreddit was marked as NSFW. (in the future this will check if its an nsfw channel, and if it is, then this check will be bypassed.)")
            return

        em = Embed(title=name, timestamp=ctx.message.created_at)
        em.set_image(url=url)

        await ctx.send(embed=em)

    @command(aliases=['crappystuff'])
    async def stupidstuff(self, ctx: Context) -> None:
        """Get some memes from r/crappydesign."""
        subreddit = await self.bot.reddit.subreddit("crappydesign")
        all_subs = []
        async for submission in subreddit.hot(limit=100):
            all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        url = random_sub.url

        if random_sub.over_18:
            await ctx.send("That post from that subreddit was marked as NSFW. (in the future this will check if its an nsfw channel, and if it is, then this check will be bypassed.)")
            return

        em = Embed(title=name, timestamp=ctx.message.created_at)
        em.set_image(url=url)

        await ctx.send(embed=em)

    @command(aliases=['truth'])
    async def technicallythetruth(self, ctx: Context) -> None:
        """Get some memes from r/technicallythetruth."""
        async with ctx.typing():
            subreddit = await self.bot.reddit.subreddit("technicallythetruth")
            all_subs = []
            async for submission in subreddit.hot(limit=100):
                all_subs.append(submission)

            random_sub = random.choice(all_subs)

            name = random_sub.title
            url = random_sub.url

            if random_sub.over_18:
                await ctx.send("That post from that subreddit was marked as NSFW. (in the future this will check if its an nsfw channel, and if it is, then this check will be bypassed.)")
                return
            else:
                em = Embed(title=name, timestamp=ctx.message.created_at)
                em.set_image(url=url)

        await ctx.send(embed=em)


def setup(bot: Client) -> None:
    """Setup function for cog."""
    bot.add_cog(ImageDiscord(bot))
