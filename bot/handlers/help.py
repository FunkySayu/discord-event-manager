"""Implements a help command listing the available commands."""

from __future__ import annotations

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

from typing import List, TYPE_CHECKING

import discord

from bot.handlers.base import CommandHandler

if TYPE_CHECKING:
    from bot.bot import WowrganizerBot


class CommandHelp(CommandHandler):
    """Lists the events happening this week."""

    COMMAND = 'help'

    def __init__(self, bot: WowrganizerBot):
        self._bot = bot

    async def handle(self, message: discord.Message):
        """Displays the list of commands available with the documentation."""
        all_handlers = self._bot.handlers
        commands = sorted(all_handlers.keys())
        help_text: List[str] = []
        for command in commands:
            doc = all_handlers[command].documentation()
            if doc is None:
                help_text.append(':: %s' % command)
            else:
                help_text.append(':: %s\n%s' % (command, doc))
        await message.channel.send("\n\n".join(help_text))
