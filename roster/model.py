"""Internal roster representation."""

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

import re

from enum import Enum
from typing import Set, List, Dict, Optional

from ui.mod_wow.static import WowPlayableClass, WowPlayableSpec


class Character:
    """Represents a character owned by a player.

    :attr server: Character's server name.
    :attr name: Character in-game name.
    :attr klass: Character class
    :attr playable_roles: Roles the player is able to play.
    """
    server: str
    name: str
    klass: WowPlayableClass
    playable_roles: List[WowPlayableSpec]

    def __init__(self, server: str, name: str, klass: WowPlayableClass,
                 playable_roles: Optional[List[WowPlayableSpec]] = None):
        self.server = server
        self.name = name
        self.klass = klass
        self.playable_roles = (playable_roles is not None
                               and playable_roles
                               or WowPlayableClass.get_all_roles(klass))

    def __repr__(self):
        """Returns a debugging representation of the character."""
        return f'<Character {self.server}/{self.name} ({self.klass.value})>'


_DISCORD_HANDLE_RE = re.compile(r'^[a-zA-Z]+#\d{4}$')


class Player:
    """Represents a player, which may own one or more characters.

    :attr discord_handle: A discord handle, matching DISCORD_HANDLE_RE
    :attr discord_uuid: The UUID of the player
    :attr characters: List of characters the player is able to play."""
    discord_handle: str  #
    discord_uuid: str  # The UUID of the player
    characters: List[Character]  # List of character this player owns.

    def __init__(self, discord_handle: str, discord_uuid: str,
                 characters: List[Character] = None):
        if not _DISCORD_HANDLE_RE.match(discord_handle):
            raise ValueError((
                "The provided discord_handle is not matching a valid"
                "handle: {}").format(discord_handle))
        self.discord_handle = discord_handle
        self.discord_uuid = discord_uuid
        self.characters = characters is not None and characters or []

    def __repr__(self):
        return '<Player {} ({} characters)>'.format(
            self.discord_handle, len(self.characters))

    def get_playable_roles(self) -> Set[WowPlayableSpec]:
        """Returns all the roles the player is able to play."""
        roles = set()
        for character in self.characters:
            for role in character.playable_roles:
                roles.add(role)
        return roles
