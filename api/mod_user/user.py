"""Database model declaration for an application user."""

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

from enum import Enum
from flask_sqlalchemy import BaseQuery
from requests_oauthlib import OAuth2Session
from typing import List, Optional

from config.discord import api_base_url
from api.base import db, BaseSerializerMixin
from api.mod_guild.guild import Guild


class Permission(Enum):
    """Permission level of a user in regards of a guild."""
    none = 'NONE'
    visible = 'VISIBLE'
    owner = 'OWNER'

    @classmethod
    def _missing_(cls, unused_value):
        """If the permission identifier is missing, assume it is none."""
        return cls.none


class UserInGuild(db.Model, BaseSerializerMixin):
    """Creates a relationship between an user and a guild."""
    __tablename__ = 'user_in_guild'

    serialize_rules = (
        # Avoid duplicated entries.
        '-user_id', '-guild_id',
    )

    user_id = db.Column('user_id', db.Integer,
                        db.ForeignKey('user.id'), primary_key=True)
    guild_id = db.Column('guild_id', db.Integer,
                         db.ForeignKey('guild.id'), primary_key=True)

    user = db.relationship('User', uselist=False)
    guild = db.relationship('Guild', uselist=False)

    permission = db.Column(db.Enum(Permission))

    def __init__(self, user: User, guild: Guild, permission=Permission.none):
        self.user_id = user.id
        self.guild_id = guild.id
        self.permission = permission


class User(db.Model, BaseSerializerMixin):
    """A Discord user.

    :attr id: Discord user's unique ID, used as primary key for storage.
    :attr date_created: The moment the guild was registered in our storage.
    :attr date_modified: The last update performed on our storage.
    :attr username: The Discord username.
    :attr discriminator: The 4 digit string allowing to make friend request.
    :attr avatar: User's avatar ID.
    :attr relationships: List of guild the user is part of.
    """
    __tablename__ = 'user'

    # Automatically created by db.Model but clarifying existence for mypy.
    query: BaseQuery

    # Serialization options
    serialize_rules = (
        # Fields computed from the record.
        'icon_url',
        # Fields not exposed to the frontend.
        '-date_created', '-date_modified', '-avatar',
        # Avoid circular dependencies.
        '-relationships.user', '-relationships.guild.users',
    )

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(
        db.DateTime,
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    username = db.Column(db.String)
    discriminator = db.Column(db.String)
    avatar = db.Column(db.String)

    # Relationships
    relationships = db.relationship('UserInGuild', uselist=True)

    def __init__(self, id: int):
        self.id = id

    @property
    def icon_url(self) -> Optional[str]:
        """Returns the URL to the icon of the user, if any."""
        if self.avatar is None:
            return None
        url = f'/avatars/{self.id}/{self.avatar}.png?size=1024'
        return str(discord.Asset(state=None, url=url))

    @classmethod
    def from_oauth_discord(cls, session: OAuth2Session):
        """Gets the values from the Discord record of a guild."""
        oauth_user = session.get(api_base_url + '/users/@me').json()
        # Try to retrieve the latest record of the user, otherwise
        # create a record.
        id = int(oauth_user.get('id'))
        user = cls.query.filter_by(id=id).one_or_none()
        if user is None:
            user = cls(id)
        user.username = oauth_user.get('username')
        user.discriminator = oauth_user.get('discriminator')
        user.avatar = oauth_user.get('avatar')
        user.resync_guild_relationships(session)
        return user

    def resync_guild_relationships(self, session: OAuth2Session):
        """Re-syncs the relationships of a user to its guilds."""
        oauth_guilds = session.get(api_base_url + '/users/@me/guilds').json()
        oauth_by_id = {g.get('id'): g for g in oauth_guilds}

        relationships: List[UserInGuild] = []

        # Get the stored guilds matching with the ones the user belongs to
        # and refresh the relationship.
        matching = Guild.query.filter(Guild.id.in_(
            tuple(oauth_by_id.keys()))).all()
        for guild in matching:
            oauth_guild = oauth_by_id[str(guild.id)]
            permission = Permission.visible
            if oauth_guild.get('owner'):
                permission = Permission.owner
            relationships.append(UserInGuild(self, guild, permission))

        # User is now complete. Remove all previous relationships and
        # update them.
        db.session.query(UserInGuild).filter_by(user_id=self.id).delete()
        db.session.add(self)
        db.session.add_all(relationships)
        db.session.commit()
