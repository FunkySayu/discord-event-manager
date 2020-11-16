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

from api.mod_wow.realm import WowRealm
from api.mod_wow.region import Region


TESTDATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'testdata')


class TestWowPlayableSpecModel(unittest.TestCase):
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

        spec = WowRealm.create_from_api(mock, Region.eu, 'argent-dawn')

        mock.get_realm.assert_called_with('eu', 'dynamic-eu', 'argent-dawn', locale='en_US')
        self.assertEqual(spec.id, 536)
        self.assertEqual(spec.name, 'Argent Dawn')
        self.assertEqual(spec.slug, 'argent-dawn')
        self.assertEqual(spec.region, Region.eu)
        self.assertEqual(spec.timezone_name, 'Europe/Paris')
