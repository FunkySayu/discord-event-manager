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
from typing import Set, List, Dict


class CharacterRole(Enum):
    """List of possible roles in the game."""
    TANK = "TANK"
    HEALER = "HEALER"
    DPS = "DPS"


class CharacterClass(Enum):
    """List of supported classes in the game."""
    DEATH_KNIGHT = "Death Knight"
    DEMON_HUNTER = "Demon Hunter"
    DRUID = "Druid"
    HUNTER = "Hunter"
    MAGE = "Mage"
    MONK = "Monk"
    PALADIN = "Paladin"
    PRIEST = "Priest"
    ROGUE = "Rogue"
    SHAMAN = "Shaman"
    WARLOCK = "Warlock"
    WARRIOR = "Warrior"

    @staticmethod
    def get_all_roles(klass: 'CharacterClass') -> List[CharacterRole]:
        if klass not in _CLASS_SUPPORTED_ROLES:
            raise ValueError("No roles registered for this class.")
        return _CLASS_SUPPORTED_ROLES[klass]


# List of roles supported by class.
_CLASS_SUPPORTED_ROLES: Dict[CharacterClass, CharacterRole] = {
    CharacterClass.DEATH_KNIGHT: [CharacterRole.TANK, CharacterRole.DPS],
    CharacterClass.DEMON_HUNTER: [CharacterRole.TANK, CharacterRole.DPS],
    CharacterClass.DRUID: [CharacterRole.TANK, CharacterRole.HEALER, CharacterRole.DPS],
    CharacterClass.HUNTER: [CharacterRole.DPS],
    CharacterClass.MAGE: [ CharacterRole.DPS],
    CharacterClass.MONK: [CharacterRole.TANK, CharacterRole.HEALER, CharacterRole.DPS],
    CharacterClass.PALADIN: [CharacterRole.TANK, CharacterRole.HEALER, CharacterRole.DPS],
    CharacterClass.PRIEST: [CharacterRole.HEALER, CharacterRole.DPS],
    CharacterClass.ROGUE: [CharacterRole.DPS],
    CharacterClass.SHAMAN: [CharacterRole.HEALER, CharacterRole.DPS],
    CharacterClass.WARLOCK: [CharacterRole.DPS],
    CharacterClass.WARRIOR: [CharacterRole.TANK, CharacterRole.DPS],
}

class Character:
    """Represents a character owned by a player.

    :attr server: Character's server name.
    :attr name: Character in-game name.
    :attr klass: Character class
    :attr playable_roles: Roles the player is able to play.
    """
    server: string
    name: string
    klass: CharacterClass
    playable_roles: List[CharacterRole]

    def __init__(self, server: string, name: string, klass: CharacterClass, playable_roles: List[CharacterRole] = None):
        self.server = server
        self.name = name
        self.klass = klass
        self.playable_roles = playable_roles is not None and playable_roles or CharacterClass.get_all_roles(klass)

    def __repr__(self):
        """Returns a debugging representation of the character."""
        return f'<Character %s/%s>'


_DISCORD_HANDLE_RE = re.compile(r'^[a-zA-Z]+#\d{4}$')


class Player:
    """Represents a player, which may own one or more characters.

    :attr discord_handle: A discord handle, matching DISCORD_HANDLE_RE
    :attr discord_uuid: The UUID of the player
    :attr characters: List of characters the player is able to play."""
    discord_handle: string  #
    discord_uuid: string  # The UUID of the player
    characters: List[Character]  # List of character this player owns.

    def __init__(self, discord_handle: string, discord_uuid: string, characters: List[Character] = None):
        if not _DISCORD_HANDLE_RE.match(discord_handle):
            raise ValueError("The provided discord_handle is not matching a valid handle: {}".format(discord_handle))
        self.discord_handle = discord_handle
        self.discord_uuid = discord_uuid
        self.characters = characters is not None and characters or []

    def get_playable_roles(self) -> Set[CharacterRole]:
        """Returns all the roles the player is able to play."""
        roles = set()
        for character in self.characters:
            for role in character.playable_roles:
                roles.add(role)
        return roles
