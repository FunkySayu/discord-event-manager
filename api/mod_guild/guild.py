"""Database model declaration for a guild and a WoW guild."""

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

import discord

from wowapi import WowApi

from flask_sqlalchemy import BaseQuery

from api.base import db, BaseSerializerMixin
from api.mod_wow.region import Region
from api.mod_wow.static import WowFaction


class Guild(db.Model, BaseSerializerMixin):
    """A Discord server supported by the bot.

    The Discord guild (aka server) is the most granular group of player
    existing on the app. A group of player cannot exist if it is not
    associated with a discord server.

    The Discord guild may link itself to a World of Warcraft guild. As
    long as this pairing is not done, the guild cannot be used by the app
    to schedule events.

    :attr id: Discord's unique ID, used as primary key for storage.
    :attr date_created: The moment the guild was registered in our storage.
    :attr date_modified: The last update performed on our storage.
    :attr discord_name: The name of the guild as per Discord.
    :attr icon_url: Address of the Discord Icon representing this server.
    :attr bot_present: Whether the bot is present in the discord guild.
    """
    __tablename__ = 'guild'

    # Automatically created by db.Model but clarifying existence for mypy.
    query: BaseQuery

    # Serialization options
    serialize_rules = ('-wow_guild_id',)

    id = db.Column(db.String, primary_key=True)
    date_created = db.Column(
        db.DateTime,
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    discord_name = db.Column(db.String)
    icon_url = db.Column(db.String)
    bot_present = db.Column(db.Boolean)

    # Relationships
    wow_guild_id = db.Column(db.Integer, db.ForeignKey('wow_guild.id'))
    wow_guild = db.relationship('WowGuild', uselist=False, back_populates='guild')
    events = db.relationship('Event', uselist=True, back_populates='guild')

    def __init__(self, id: str):
        self.id = id

    def resync_from_discord_guild(self, discord_guild: discord.Guild):
        """Gets the values from the Discord record of a guild."""
        self.id = str(discord_guild.id)
        self.discord_name = discord_guild.name
        self.icon_url = str(discord_guild.icon_url)
        self.bot_present = True


class AssociatedCharacter(db.Model, BaseSerializerMixin):
    """A character belonging to a player associated to a WoW guild."""
    __tablename__ = 'associated_character'

    # Serialization options
    serialize_rules = (
        '-user_id',
        '-guild_id',
        '-character_id',
        # Remove circular dependency from the relationships.
        '-character.associated_user_in_guild',
        '-user_in_guild.associated_characters',
    )

    user_id = db.Column(db.Integer,
                        db.ForeignKey('user_in_guild.user_id'),
                        primary_key=True)
    guild_id = db.Column(db.Integer,
                         db.ForeignKey('user_in_guild.guild_id'),
                         primary_key=True)
    character_id = db.Column(db.Integer,
                             db.ForeignKey('wow_characters.id'),
                             primary_key=True)

    user_in_guild = db.relationship(
        'UserInGuild',
        foreign_keys=[user_id, guild_id],
        backref='associated_characters',
        uselist=False,
        primaryjoin="(AssociatedCharacter.user_id == UserInGuild.user_id) & (AssociatedCharacter.guild_id == UserInGuild.guild_id)")
    character = db.relationship('WowCharacter')

class WowGuild(db.Model, BaseSerializerMixin):
    """A World of Warcraft guild.

    This object contains a refined version of the object returned by the
    Blizzard API. Guild profiles may change on a fairly low frequency.
    Consumers of this model should consider refreshing the data on a
    defined period.

    All localized values are using the en_US locale.

    :attr id: The guild's ID, as returned from the WoW API.
    :attr date_created: The moment the guild was registered in our storage.
    :attr date_modified: The last update performed on our storage.
    :attr region: The guild's region (eu, na...).
    :attr realm_slug: The slug name of the guild's realm.
    :attr name_slug: The slug name of the guild.
    :attr realm_name: The localized version of the guild's realm.
    :attr name: The localized version of the guild name.
    :attr faction: Faction the guild is into.
    :attr icon_url: Address of the icon of this guild.
    :attr guild: back populated guild associated to this wow guild.
    """
    __tablename__ = 'wow_guild'

    # Automatically created by db.Model but clarifying existence for mypy.
    query: BaseQuery

    # Serialization options
    serialize_rules = (
        '-id',
        # Remove circular dependency from the relationships.
        '-guild',
    )

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(
        db.DateTime,
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    region = db.Column(db.Enum(Region))
    realm_slug = db.Column(db.String)
    name_slug = db.Column(db.String)

    realm_name = db.Column(db.String)
    name = db.Column(db.String)
    faction = db.Column(db.Enum(WowFaction))
    icon_url = db.Column(db.String)

    # Relationships
    guild = db.relationship('Guild', uselist=False,
                            back_populates='wow_guild')

    def __init__(self, id: int, region: Region,
                 realm_slug: str, name_slug: str):
        self.id = id
        self.region = region
        self.realm_slug = realm_slug
        self.name_slug = name_slug

    def __repr__(self):
        return '<Guild %r/%r/%r (#%r)>' % (self.region, self.realm_slug,
                                           self.name_slug, self.id)

    @classmethod
    def create_from_api(cls, handler: WowApi, region: Region,
                        realm_slug: str, name_slug: str) -> WowGuild:
        """Creates a WowGuild object from the API endpoint."""
        data = handler.get_guild(
            region.value, region.profile_namespace, realm_slug, name_slug,
            locale='en_US')
        guild = cls(data['id'], region, realm_slug, name_slug)
        guild.faction = WowFaction(data['faction']['type'])
        guild.name = data['name']
        guild.realm_name = data['realm']['name']

        crest_data = handler.get_guild_crest_emblem_media(
            region.value, region.static_namespace,
            data['crest']['emblem']['id'])
        guild.icon_url = crest_data['assets'][0]['value']

        return guild
