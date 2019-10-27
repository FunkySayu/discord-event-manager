"""Reveals a true beauty on your discord channel."""

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

@handles('eighth_wonder')
async def command_eighth_wonder(message: discord.Message):
    """You just can't handle it"""
    with open("assets/eighth_wonder") as f:
        await message.channel.send(
          '```\n' +
          f.read() +
          '```\n')
