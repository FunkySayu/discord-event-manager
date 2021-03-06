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
from api.mod_wow.realm import WowRealm
from api.mod_wow.region import Region


TESTDATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'testdata')


class TestWowPlayableSpecModel(DatabaseTestFixture, unittest.TestCase):
    """Checks creation of a wow playable spec."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        with open(os.path.join(TESTDATA_DIR,
                               'get_realm.json')) as f:
            cls.REALM_DATA = json.load(f)

    def test_create_playable_spec_from_api(self):
        """Test creation from the WoW API results."""
        mock = unittest.mock.MagicMock()
        mock.get_realm.return_value = self.REALM_DATA

        realm = WowRealm.create_from_api(mock, Region.eu, 'argent-dawn')

        mock.get_realm.assert_called_with('eu', 'dynamic-eu', 'argent-dawn', locale='en_US')
        self.assertEqual(realm.id, 536)
        self.assertEqual(realm.name, 'Argent Dawn')
        self.assertEqual(realm.slug, 'argent-dawn')
        self.assertEqual(realm.region, Region.eu)
        self.assertEqual(realm.timezone_name, 'Europe/Paris')

    def test_get_or_create_queries_api(self):
        """Tests the realm is queried if not available in database."""
        mock = unittest.mock.MagicMock()
        mock.get_realm.return_value = self.REALM_DATA

        realm = WowRealm.get_or_create(mock, Region.eu, 'argent-dawn')

        mock.get_realm.assert_called_with('eu', 'dynamic-eu', 'argent-dawn', locale='en_US')
        self.assertEqual(realm.id, 536)

    def test_get_or_create_uses_cache(self):
        """Tests the realm is queried from database if available there."""
        mock = unittest.mock.MagicMock()
        mock.get_realm.return_value = self.REALM_DATA
        stored_realm = WowRealm(id=536, slug='argent-dawn', region=Region.eu)
        self.db.session.add(stored_realm)

        realm = WowRealm.get_or_create(mock, Region.eu, 'argent-dawn')

        mock.get_realm.assert_not_called()
        self.assertEqual(realm.id, 536)
