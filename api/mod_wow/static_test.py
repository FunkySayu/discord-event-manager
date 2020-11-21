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
from api.mod_wow.static import WowRole, WowPlayableClass, WowPlayableSpec


TESTDATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'testdata')


class TestWowPlayableSpecModel(DatabaseTestFixture, unittest.TestCase):
    """Checks creation of a wow playable spec."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        with open(os.path.join(TESTDATA_DIR,
                               'get_playable_spec__268.json')) as f:
            cls.BREWMASTER_SPEC_DATA = json.load(f)

    def test_create_playable_spec_from_api(self):
        """Test creation from the WoW API results."""
        mock = unittest.mock.MagicMock()
        mock.get_playable_specialization.return_value = self.BREWMASTER_SPEC_DATA

        spec = WowPlayableSpec.create_from_api(mock, 268)

        mock.get_playable_specialization.assert_called_with('us', 'static-us', 268, locale='en_US')
        self.assertEqual(spec.id, 268)
        self.assertEqual(spec.name, 'Brewmaster')
        self.assertEqual(spec.role, WowRole.tank)

    def test_get_or_create_queries_api(self):
        """Tests the realm is queried if not available in database."""
        mock = unittest.mock.MagicMock()
        mock.get_playable_specialization.return_value = self.BREWMASTER_SPEC_DATA

        spec = WowPlayableSpec.get_or_create(mock, 268)

        mock.get_playable_specialization.assert_called_with('us', 'static-us', 268, locale='en_US')
        self.assertEqual(spec.id, 268)
        self.assertEqual(spec.name, 'Brewmaster')
        self.assertEqual(spec.role, WowRole.tank)

    def test_get_or_create_uses_cache(self):
        """Tests the realm is queried from database if available there."""
        mock = unittest.mock.MagicMock()
        mock.get_playable_specialization.return_value = self.BREWMASTER_SPEC_DATA
        stored_spec = WowPlayableSpec(id=268, name='Brewmaster', role=WowRole.tank)
        self.db.session.add(stored_spec)

        spec = WowPlayableSpec.get_or_create(mock, 268)

        mock.get_realm.assert_not_called()
        self.assertEqual(spec.id, 268)


class TestWowPlayableClassModel(DatabaseTestFixture, unittest.TestCase):
    """Checks creation of a wow playable spec."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        with open(os.path.join(TESTDATA_DIR,
                               'get_playable_class__10.json')) as f:
            cls.MONK_CLASS_DATA = json.load(f)
        cls.MONK_SPECS_DATA = {}
        with open(os.path.join(TESTDATA_DIR,
                               'get_playable_spec__268.json')) as f:
            cls.MONK_SPECS_DATA[268] = json.load(f)
        with open(os.path.join(TESTDATA_DIR,
                               'get_playable_spec__269.json')) as f:
            cls.MONK_SPECS_DATA[269] = json.load(f)
        with open(os.path.join(TESTDATA_DIR,
                               'get_playable_spec__270.json')) as f:
            cls.MONK_SPECS_DATA[270] = json.load(f)

    def create_mock_api(self) -> unittest.mock.MagicMock:
        """Creates a mock API providing data about the Monk class."""
        def playable_spec_wrapper(unused_region, unused_profile, id, *args, **kwargs):
            return self.MONK_SPECS_DATA[id]

        mock = unittest.mock.MagicMock()
        mock.get_playable_specialization.side_effect = playable_spec_wrapper
        mock.get_playable_class.return_value = self.MONK_CLASS_DATA
        return mock

    def test_create_playable_class_from_api(self):
        """Test creation from the WoW API results."""
        mock = self.create_mock_api()

        klass = WowPlayableClass.create_from_api(mock, 10)

        mock.get_playable_class.assert_called_with('us', 'static-us', 10, locale='en_US')
        self.assertEqual(klass.id, 10)
        self.assertEqual(klass.name, 'Monk')
        self.assertEqual([s.name for s in klass.specs], ['Brewmaster', 'Windwalker', 'Mistweaver'])

    def test_get_or_create_queries_api(self):
        """Tests the realm is queried if not available in database."""
        mock = self.create_mock_api()

        klass = WowPlayableClass.get_or_create(mock, 10)

        mock.get_playable_class.assert_called_with('us', 'static-us', 10, locale='en_US')
        self.assertEqual(klass.id, 10)
        self.assertEqual(klass.name, 'Monk')
        self.assertEqual([s.name for s in klass.specs], ['Brewmaster', 'Windwalker', 'Mistweaver'])

    def test_get_or_create_uses_cache(self):
        """Tests the realm is queried from database if available there."""
        mock = self.create_mock_api()
        stored_class = WowPlayableClass(id=10, name='Monk', specs=[
            WowPlayableSpec(id=268, name='Brewmaster'),
            WowPlayableSpec(id=269, name='Windwalker'),
            WowPlayableSpec(id=270, name='Mistweaver')
        ])
        self.db.session.add(stored_class)

        klass = WowPlayableClass.get_or_create(mock, 10)

        mock.get_playable_class.assert_not_called()
        self.assertEqual(klass.id, 10)
        self.assertEqual(klass.name, 'Monk')
        self.assertEqual([s.name for s in klass.specs], ['Brewmaster', 'Windwalker', 'Mistweaver'])
