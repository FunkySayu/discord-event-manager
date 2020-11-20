"""Form definition for the mod_user controllers."""

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

from wowapi import WowApi

from api.common.forms import EnumField
from wtforms import Form, StringField

from api.mod_wow.region import Region
from api.mod_wow.character import WowCharacter
from api.mod_wow.realm import WowRealm


class CharacterAssociationForm(Form):
    """Field checker for creating an event."""
    region = EnumField('Repetition frequency', enum=Region)
    character_slug = StringField('Character Slug')
    realm_slug = StringField('Realm Slug')

    def get_character(self, handler: WowApi) -> WowCharacter:
        """Converts the data provided in the form to an event."""
        realm = WowRealm.query.filter_by(
            region=self.region.data, slug=self.realm_slug.data).one_or_none()
        if realm is None:
            realm = WowRealm.create_from_api(
                handler, self.region.data, self.realm_slug.data)

        character = WowCharacter.query.filter_by(
            realm_id=realm.id, name=self.character_slug.data).one_or_none()
        if character is None:
            character = WowCharacter.create_from_api(
                handler, realm, self.character_slug.data)

        return character
