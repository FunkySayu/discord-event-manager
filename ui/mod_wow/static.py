"""Generally static data from the WoW API.

This file interfaces with data that are most of the time a one-time-load, coming
form the Game Data APIs.

See also: https://develop.battle.net/documentation/world-of-warcraft/game-data-apis
"""

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

from enum import Enum
from wowapi import WowApi

from flask_sqlalchemy import BaseQuery

from ui.base import db, BaseSerializerMixin
from ui.mod_wow.region import DEFAULT_REGION


class WowFaction(Enum):
    """World of Warcraft role a spec can implement."""
    horde = "HORDE"
    alliance = "ALLIANCE"


class WowRole(Enum):
    """World of Warcraft role a spec can implement."""
    dps = "DAMAGE"
    heal = "HEALER"
    tank = "TANK"


class WowPlayableSpec(db.Model, BaseSerializerMixin):
    """Represents a playable spec.

    :attr id: ID of the playable spec, matching Blizzard's Game API ID.
    :attr name: the name of the spec (in en_US locale).
    :attr role: the world of warcraft role associated to this spec.
    :attr klass: the class it relates to.
    """
    __tablename__ = 'wow_specs'

    # Automatically created by db.Model but clarifying existence for mypy.
    query: BaseQuery

    # Serialization options
    serialize_rules = ('-klass', '-klass_id')

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(
        db.DateTime,
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    name = db.Column(db.String)
    role = db.Column(db.Enum(WowRole))
    klass_id = db.Column(db.Integer, db.ForeignKey('wow_classes.id'))
    klass = db.relationship('WowPlayableClass', uselist=False, back_populates='specs')

    def __init__(self, id: int, name: str, role: WowRole):
        self.id = id
        self.name = name
        self.role = role

    @classmethod
    def create_from_api(cls, handler: WowApi, spec_id: int) -> WowPlayableSpec:
        """Creates a WowPlayableClass from the data returned by the WoW API"""
        data = handler.get_playable_specialization(
            DEFAULT_REGION.value, DEFAULT_REGION.static_namespace, spec_id,
            locale='en_US')
        return cls(data['id'], data['name'], WowRole(data['role']['type']))


class WowPlayableClass(db.Model, BaseSerializerMixin):
    """A world of warcraft playable class.

    :attr id: ID of the playable class, matching Blizzard's Game API one.
    :attr name: the name of the class in en_US locale.
    :attr specs: the list of playable specs for this class.
    """
    __tablename__ = 'wow_classes'

    # Automatically created by db.Model but clarifying existence for mypy.
    query: BaseQuery

    # Serialization options
    serialize_rules = ('-wow_guild_id',)

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(
        db.DateTime,
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    name = db.Column(db.String)
    specs = db.relationship('WowPlayableSpec', uselist=True, back_populates='klass')

    @classmethod
    def create_from_api(cls, handler: WowApi, class_id: int) -> WowPlayableClass:
        """Creates a WowPlayableClass from the data returned by the WoW API"""
        data = handler.get_playable_class(
            DEFAULT_REGION.value, DEFAULT_REGION.static_namespace, class_id,
            locale='en_US')
        klass = cls()
        klass.id = data['id']
        klass.name = data['name']
        klass.specs = [WowPlayableSpec.create_from_api(handler, spec['id']) for spec in data['specializations']]
        return klass
