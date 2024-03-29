"""Aperture Expieriments - A General Purpose Discord Bot.
    Copyright (C) 2023  cserver45

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import configparser
import os
from typing import Tuple

import aiohttp
import discord
import motor.motor_asyncio
from discord.ext import commands  # pylint: disable=E0611
from discord.ext.commands import (CommandNotFound, CommandOnCooldown, Context,
                                   MissingPermissions, MissingRequiredArgument,
                                   NoPrivateMessage, NotOwner, UserInputError)

# monkypatching stuff

# discord.gateway.DiscordWebSocket.identify.payload["d"]["$browser"] = 'Discord Android'
# discord.gateway.DiscordWebSocket.identify.payload["d"]["$device"] = 'Android'

train = r'''
   ___     _ __                    _                                         _             _
  /   \   | '_ \   ___      _ _   | |_    _  _      _ _    ___      o O O   | |    __ _   | |__     ___
  | - |   | .__/  / -_)    | '_|  |  _|  | +| |    | '_|  / -_)    o        | |   / _` |  | '_ \   (_-<
  |_|_|   |_|__   \___|   _|_|_   _\__|   \_,_|   _|_|_   \___|   TS__[O]  _|_|_  \__,_|  |_.__/   /__/_
_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| {======|_|"""""|_|"""""|_|"""""|_|"""""|
"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'
'''


class Bot(commands.AutoShardedBot):
    """Custom Bot class made mainly for neatness."""

    IGNORE_ERRS = (
        MissingRequiredArgument,
        CommandOnCooldown,
        CommandNotFound,
        NoPrivateMessage,
        MissingPermissions,
        UserInputError,
        NotOwner,
    )

    # it works anyway (created at runtime?)
    # pylint: disable=E1101
    parser = argparse.ArgumentParser(description='A General Purpose Discord bot.')
    parser.add_argument('--loglevel',
                        '-ll',
                        type=str,
                        choices=['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO',
                        help='Sets the log level. default is INFO.'
                        )
    parser.add_argument('--token',
                        '-t',
                        type=str,
                        default='protoken',
                        help='Sets the token type. defalt is protoken. Options: protoken, testtoken'
                        )
    parser.add_argument('--dboveride',
                        action=argparse.BooleanOptionalAction,  # type: ignore
                        help='Overides the db address for testing. default is False'
                        )
    argus = parser.parse_args()

    # pylint: enable=E1101
    # pylint: disable=R0904

    def __init__(self, *args: list, **kwargs: dict) -> None:
        """Init function."""
        #asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        # configuration file parser
        self.config = configparser.ConfigParser()
        self.config.read('config/bot.conf')

        if self.argus.token == "protoken":
            self.config["mongodb"]["passwd"] = self.config["mongodb"]["passwd"].replace("authSource=aperturelabsbot", "authSource=admin")

        # then, define the activity type var
        activity_type = discord.Activity(type=discord.ActivityType.playing,
                                          name='Starting up...'
                                         )

        # also define intents
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        # for that custom function for prod
        self.db_pass = self.config["mongodb"]["passwd"]

        # mongodb stuff
        client = motor.motor_asyncio.AsyncIOMotorClient(str(self.config["mongodb"]["passwd"]))
        self.db = client.aperturelabsbot

        # init the parent class (AutoShardedBot)
        super().__init__(*args,
                         status=discord.Status.idle,
                         activity=activity_type,
                         intents=intents,
                         case_insensitive=True,
                         max_messages=1500,
                         command_prefix=".",
                         **kwargs
                         )

        print(train)

    async def on_command_error(self, _: Context, error: Exception) -> None:  # pylint: disable=W0221
        """Call when a command has an error."""
        if isinstance(error, self.IGNORE_ERRS):
            pass
        else:
            raise error

    @staticmethod
    def convert_time_custom(time: str) -> int:
        """Convert prefix times to seconds."""
        pos = ["s", "m", "h", "d"]

        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except (TypeError, ValueError):
            return -2

        return val * time_dict[unit]

    async def setup_hook(self):
        """Interior function that is run before the bot is started."""
        # load all the other cogs
        # init the aiohttp session
        self.session = aiohttp.ClientSession()

        testbannedcogs = ("welcome.py")

        for f in os.listdir("./cogs"):
            if f.endswith('.py'):
                if self.argus.token == 'testtoken':
                    if f in testbannedcogs:
                        continue
                    else:
                        await bot.load_extension(f'cogs.{f[:-3]}')
                else:
                    await bot.load_extension(f'cogs.{f[:-3]}')

        self.tree.copy_global_to(guild=discord.Object(id=777203561708126208))
        await self.tree.sync(guild=discord.Object(id=777203561708126208))

    # pylint: disable=W0221

    def run(self) -> None:
        """Run the bot."""
        if self.argus.token == 'testtoken':
            token = self.config["main"]["canarytoken"]
        elif self.argus.token == 'protoken':
            token = self.config["main"]["token"]
        else:
            raise Exception('Not a vailid token option')

        super().run(token, reconnect=True)

    # pylint: enable=W0221

    @property
    def command_count(self) -> int:
        """Return the amount of commands that the bot has."""
        return len(self.commands)

    @property
    def cog_count(self) -> int:
        """Return the amount of cogs that are currently loaded."""
        return len([c for c in self.cogs])  # pylint: disable=R1721

    @property
    def guild_count(self) -> int:
        """Return the guild count."""
        return len(self.guilds)

    @property
    def total_member_count(self) -> Tuple:
        """Return the total members, and total guilds the bot is in."""
        bot_in_guilds = 0
        members_total = 0
        for guild in self.guilds:
            for _ in guild.members:
                members_total += 1
            bot_in_guilds += 1
        actual_members_total = members_total - bot_in_guilds
        return (actual_members_total, bot_in_guilds)


bot = Bot()
bot.run()
