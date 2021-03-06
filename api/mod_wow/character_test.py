import unittest

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

import json
import os
import unittest.mock

from api.common.testing import DatabaseTestFixture
from api.mod_wow.character import WowCharacter
from api.mod_wow.region import Region
from api.mod_wow.realm import WowRealm
from api.mod_wow.static import WowFaction


TESTDATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'testdata')


class TestWowPlayableSpecModel(DatabaseTestFixture, unittest.TestCase):
    """Checks creation of a wow playable spec."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        with open(os.path.join(TESTDATA_DIR,
                               'get_character__146666340.json')) as f:
            cls.CHARACTER_DATA = json.load(f)

    def test_create_playable_spec_from_api(self):
        """Test creation from the WoW API results."""
        mock = unittest.mock.MagicMock()
        mock.get_character_profile_summary.return_value = self.CHARACTER_DATA

        realm = WowRealm(id=536, region=Region.eu, name='Argent Dawn',
                         slug='argent-dawn', timezone_name='Europe/Paris')
        character = WowCharacter.create_from_api(mock, realm, 'Funkypewpew')

        mock.get_character_profile_summary.assert_called_with(
            'eu', 'profile-eu', 'argent-dawn', 'Funkypewpew', locale='en_US')
        self.assertEqual(character.id, '146666340')
        self.assertEqual(character.name, 'Funkypewpew')
        self.assertEqual(character.realm_id, 536)
        self.assertEqual(character.faction, WowFaction.alliance)
        self.assertEqual(character.klass_id, 3)
        self.assertEqual(character.active_spec_id, 253)
        self.assertEqual(character.average_ilvl, 136)
        self.assertEqual(character.equipped_ilvl, 135)

    def test_get_or_create_queries_api(self):
        """Tests the character is queried if not available in database."""
        mock = unittest.mock.MagicMock()
        mock.get_character_profile_summary.return_value = self.CHARACTER_DATA

        realm = WowRealm(id=536, region=Region.eu, slug='argent-dawn')
        character = WowCharacter.get_or_create(mock, realm, 'Funkypewpew')

        mock.get_character_profile_summary.assert_called_with(
            'eu', 'profile-eu', 'argent-dawn', 'Funkypewpew', locale='en_US')
        self.assertEqual(character.id, '146666340')
        self.assertEqual(character.name, 'Funkypewpew')

    def test_get_or_create_uses_cache(self):
        """Tests the character is queried from database if available there."""
        mock = unittest.mock.MagicMock()
        mock.get_character_profile_summary.return_value = self.CHARACTER_DATA
        realm = WowRealm(id=536, region=Region.eu, slug='argent-dawn')
        stored_character = WowCharacter(id='123456', name='Funkypewpew', realm_id=realm.id, realm=realm)
        self.db.session.add(stored_character)

        character = WowCharacter.get_or_create(mock, realm, 'Funkypewpew')

        mock.get_character_profile_summary.assert_not_called()
        self.assertEqual(character.id, '123456')
        self.assertEqual(character.name, 'Funkypewpew')
