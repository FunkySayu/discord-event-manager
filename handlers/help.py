"""Implements a help command listing the available commands."""

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

from typing import List

import discord

from .registry import handles, DEFAULT_REGISTRY


@handles('help')
async def command_help(message: discord.Message):
    """Displays the list of commands available with the documentation."""
    commands = sorted(DEFAULT_REGISTRY.commands.keys())
    help_text = []  # type: List[str]
    for command in commands:
        doc = DEFAULT_REGISTRY.commands[command].__doc__
        if doc is None:
            help_text.append(':: %s' % command)
        else:
            help_text.append(':: %s\n%s' % (command, DEFAULT_REGISTRY.commands[command].__doc__))
    await message.channel.send("\n\n".join(help_text))