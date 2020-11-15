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

from ui.mod_wow.static import WowRole, WowPlayableClass, WowPlayableSpec


TESTDATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'testdata')


class TestWowPlayableSpecModel(unittest.TestCase):
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


class TestWowPlayableClassModel(unittest.TestCase):
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

    def test_create_playable_class_from_api(self):
        """Test creation from the WoW API results."""
        def playable_spec_wrapper(unused_region, unused_profile, id, *args, **kwargs):
            return self.MONK_SPECS_DATA[id]

        mock = unittest.mock.MagicMock()
        mock.get_playable_specialization.side_effect = playable_spec_wrapper
        mock.get_playable_class.return_value = self.MONK_CLASS_DATA

        klass = WowPlayableClass.create_from_api(mock, 10)

        mock.get_playable_class.assert_called_with('us', 'static-us', 10, locale='en_US')
        self.assertEqual(klass.id, 10)
        self.assertEqual(klass.name, 'Monk')
        self.assertEqual([s.name for s in klass.specs], ['Brewmaster', 'Windwalker', 'Mistweaver'])
