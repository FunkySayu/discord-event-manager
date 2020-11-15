"""Represents a realm in World of Warcraft."""

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

from flask_sqlalchemy import BaseQuery
from wowapi import WowApi
from pytz import timezone

from ui.base import db, BaseSerializerMixin
from ui.mod_wow.region import Region


class WowRealm(db.Model, BaseSerializerMixin):
    """Represents a world of warcraft realm.

    :attr id: ID of the realm, matching Blizzard's Game API ID.
    :attr name: Name of the realm, in en_US locale.
    :attr slug: Slug id of the realm, used to query related data.
    :attr region: Region this realm belongs to.
    :attr timezone_name: The server-side timezone of this realm.
    """
    __tablename__ = 'wow_realms'

    # Automatically created by db.Model but clarifying existence for mypy.
    query: BaseQuery

    # Serialization options
    serialize_rules = ('-timezone',)

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(
        db.DateTime,
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    name = db.Column(db.String)
    slug = db.Column(db.String)
    region = db.Column(db.Enum(Region))
    timezone_name = db.Column(db.String)

    def __init__(self, id: int, name: str, slug: str, region: Region, timezone_name: str):
        self.id = id
        self.name = name
        self.slug = slug
        self.region = region
        self.timezone_name = timezone_name

    @classmethod
    def create_from_api(cls, handler: WowApi, region: Region, realm_slug: str) -> WowRealm:
        """Creates a WowPlayableClass from the data returned by the WoW API"""
        data = handler.get_realm(region.value, region.dynamic_namespace, realm_slug, locale='en_US')
        return cls(data['id'], data['name'], data['slug'], region, data['timezone'])

    @property
    def timezone(self):
        """Returns the timezone object of this realm."""
        return timezone(self.timezone_name)
