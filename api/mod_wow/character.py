"""Represents a character on world of warcraft."""

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

from typing import Optional, List
from wowapi import WowApi, WowApiException
from werkzeug.exceptions import HTTPException

from flask_sqlalchemy import BaseQuery

from api.base import db, BaseSerializerMixin
from api.mod_wow.realm import WowRealm
from api.mod_wow.static import WowFaction, WowPlayableClass, WowPlayableSpec
from api.mod_wow.region import Region


class CharacerNotFoundException(WowApiException, HTTPException):
    """The requested character was not found."""
    code = 404
    character: str
    realm: WowRealm

    def __init__(self, msg: str, realm: WowRealm, character: str):
        super().__init__(msg)
        self.realm = realm
        self.character = character

class WowCharacter(db.Model, BaseSerializerMixin):
    """Represents a world of warcraft character.

    :attr id: ID of the character, matching Blizzard's Game API ID.
    :attr realm: The realm this character belongs to.
    :attr name: The name of the character.
    :attr faction: The faction of the character.
    :attr klass: The class of the character.
    :attr active_spec: Currently activated spec, updated last time the player logged out
    :attr average_ilvl: Average iLvL, as seen when the user is tagging.
    :attr equipped_ilvl: Currently equiped iLvL.
    """
    __tablename__ = 'wow_characters'

    # Automatically created by db.Model but clarifying existence for mypy.
    query: BaseQuery

    # Serialization options
    serialize_rules = ('-klass_id', '-active_spec_id','-realm_id')

    id = db.Column(db.String, primary_key=True)
    date_created = db.Column(
        db.DateTime,
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    name = db.Column(db.String)
    realm_id = db.Column(db.Integer, db.ForeignKey('wow_realms.id'))
    realm = db.relationship('WowRealm', uselist=False)
    faction = db.Column(db.Enum(WowFaction))
    klass_id = db.Column(db.Integer, db.ForeignKey('wow_classes.id'))
    klass = db.relationship(WowPlayableClass, uselist=False)
    active_spec_id = db.Column(db.Integer, db.ForeignKey('wow_specs.id'))
    active_spec = db.relationship(WowPlayableSpec, uselist=False)
    average_ilvl = db.Column(db.Integer)
    equipped_ilvl = db.Column(db.Integer)

    @classmethod
    def create_from_api(cls, handler: WowApi, realm: WowRealm, name: str) -> WowCharacter:
        """Retrieves data about a character from the wow API."""
        try:
            data = handler.get_character_profile_summary(
                realm.region.value, realm.region.profile_namespace, realm.slug,
                name.lower(), locale='en_US')
        except WowApiException as e:
            if str(e).endswith('404'):
                raise CharacerNotFoundException(str(e), realm, name)

        klass = WowPlayableClass.get_or_create(handler, data['character_class']['id'])
        return cls(
            id=str(data['id']),
            name=data['name'],
            realm_id=realm.id,
            realm=realm,
            faction=WowFaction(data['faction']['type']),
            klass=klass,
            active_spec_id=data['active_spec']['id'],
            average_ilvl=data['average_item_level'],
            equipped_ilvl=data['equipped_item_level'])

    @classmethod
    def get_or_create(cls, handler: WowApi, realm: WowRealm, name: str) -> WowCharacter:
        """Try to get a WowCharacter from the database or create it from the API."""
        character: Optional[WowCharacter] = cls.query.filter_by(
            realm_id=realm.id, name=name.title()).one_or_none()
        if character is None:
            character = cls.create_from_api(handler, realm, name)
        return character

    @classmethod
    def get_logged_user_characters(cls, handler: WowApi, token: str, region: Region) -> List[WowCharacter]:
        """Retrieves the user's character list."""
        print(region.value, region.profile_namespace, token)
        data = handler.get_account_profile_summary(region.value, region.profile_namespace, token)

        # Users may have multiple accounts in the event they have/had
        # different subscriptions.
        accounts = data.get('wow_accounts', [])
        characters: List[WowCharacter] = []
        for account in accounts:
            for character_data in account.get('characters', []):
                # The wow api has missing data when querying a character from the account-bound
                # character API, such as ilvl, active spec etc. To have the full definition
                # of the character we need to query again the character from the public API.
                realm = WowRealm.get_or_create(
                    handler, region, character_data['realm']['slug'])
                try:
                    characters.append(cls.get_or_create(handler, realm, character_data['name']))
                except CharacerNotFoundException as e:
                    pass
        return characters
