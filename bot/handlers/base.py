"""A basic handler definition. Handlers must inherit from it."""

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

from abc import ABC, abstractmethod


class CommandHandler(ABC):
    """Handles a command."""

    COMMAND = ''

    @abstractmethod
    async def handle(self, message: discord.Message):
        """Handles the provided discord message.

        Note the documentation of this method constitutes your command
        documentation, i.e. it is user visible from Discord.
        """
        raise NotImplementedError()

    def documentation(self):
        """Returns the documentation of the command handler.

        This method may be overridden for documentation generation.
        """
        return self.handle.__doc__
