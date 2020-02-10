"""A way too complicated way to register commands in a Bot."""

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

from inspect import getframeinfo, stack
from typing import Callable, Dict

CommandCallable = Callable[[discord.Message], None]


class CommandRegistry:
    """A registry stores commands created for the bot."""
    commands = {}  # type: Dict[str, CommandCallable]

    def register(self, name: str, command: CommandCallable):
        """Associates a command name to a handler.

        :raises ValueError: If a command with the same name was already
                            registered.
        """
        if name in self.commands:
            caller = getframeinfo(stack()[1][0])
            raise ValueError(
                "%s command name is already registered; "
                "last registered at %s:%d" %
                (name, caller.filename, caller.lineno))
        self.commands[name] = command


#: Default registry used to store all commands.
DEFAULT_REGISTRY = CommandRegistry()


def handles(name: str) -> Callable[[CommandCallable], CommandCallable]:
    """Registers a function as a handler of the provided command name.

    >>> from handlers import registry
    >>> @registry.handles("hello")
    >>> def hello_handler(argv: List[str], _):
    >>>     print("hello %s", " ".join(argv))

    :raises ValueError: If a command with the same name was already registered.
    """
    def decorator(func: CommandCallable) -> CommandCallable:
        DEFAULT_REGISTRY.register(name, func)
        return func
    return decorator
