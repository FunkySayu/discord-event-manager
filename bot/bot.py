"""The bot itself."""

__LICENSE__ = """
Copyright 2019 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import discord
import logging

from typing import Dict, Optional, List

from bot.handlers.base import CommandHandler
from bot.handlers.events import CommandWeekly, CommandSetTimezone
from bot.handlers.help import CommandHelp
from ui.base import app, db
from ui.mod_guild.guild import Guild


class WowrganizerBot(discord.Client):
    """Wowrganizer Discord bot interface definition.

    This class defines the main interface between Discord and the bot
    itself, listening for server-level events and clients-level ones.

    :attr _handlers: The commands the bot supports, keyed by their trigger.
    """

    handlers: Dict[str, CommandHandler]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        all_handlers = self._setup_handlers()
        self.handlers = {}
        for handler in all_handlers:
            if handler.COMMAND == '':
                raise ValueError(
                    'Handler %r has no command associated' % handler)
            if handler.COMMAND in self.handlers:
                raise ValueError(
                    'Duplicated command %s: culprit handlers are %r and %r' % (
                        handler.COMMAND, handler,
                        self.handlers[handler.COMMAND]))
            self.handlers[handler.COMMAND] = handler

    def _setup_handlers(self) -> List[CommandHandler]:
        """Called at initialization, sets up the command handlers."""
        return [
            CommandWeekly(),
            CommandSetTimezone(),
            CommandHelp(self),
        ]

    async def on_ready(self):
        """Notify we are ready to handle requests."""
        with app.app_context():
            for discord_guild in self.guilds:
                guild = Guild.query.filter_by(id=discord_guild.id).one_or_none()
                if guild is None:
                    guild = Guild(discord_guild.id)
                guild.resync_from_discord_guild(discord_guild)
                db.session.add(guild)
            db.session.commit()

    async def on_guild_join(self, discord_guild: discord.Guild):
        """Registers the guild as available in the DB."""
        logging.info('Joined guild %s', discord_guild.name)
        with app.app_context():
            guild = Guild.query.filter_by(id=discord_guild.id).one_or_none()
            if guild is None:
                guild = Guild(discord_guild.id)
            guild.resync_from_discord_guild(discord_guild)
            db.session.add(guild)
            db.session.commit()

    async def on_guild_remove(self, discord_guild: discord.Guild):
        """Un-register the guild as available in the DB."""
        logging.info('Removed from guild %s', discord_guild.name)
        with app.app_context():
            guild = Guild.query.filter_by(id=discord_guild.id).one_or_none()
            if guild is None:
                return
            db.session.delete(guild)
            db.session.commit()

    async def on_message(self, message: discord.Message):
        """Checks if a command was sent in the message for this bot."""
        if message.author == self.user:
            return
        if not message.content.startswith('!'):
            return

        command_name = message.content.partition(' ')[0][1:]
        if command_name in self.handlers:
            await self.handlers[command_name].handle(message)
        else:
            await message.channel.send('Unknown command.')


# Runtime instance management.
_instance: Optional[WowrganizerBot] = None


def get_bot_instance() -> WowrganizerBot:
    """Returns the instance of the bot."""
    global _instance
    if _instance is None:
        raise RuntimeError('Bot was not initialized')
    return _instance


def make_bot_instance(*args, **kwargs) -> WowrganizerBot:
    """Creates the single bot instance."""
    global _instance
    if _instance is not None:
        raise RuntimeError('Make instance was called twice.')
    _instance = WowrganizerBot(*args, **kwargs)
    return _instance
