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

from unittest.mock import MagicMock

from roster.sheet_integration import RosterSpreadsheet


def fake_cursor(results):
    """Creates a fake spreadsheet cursor returning the provided results."""
    mock = MagicMock()
    mock.execute.return_value = {'values': results}
    return mock


class RosterSpreadsheetTest(unittest.IsolatedAsyncioTestCase):

    async def test_supports_multiple_characters(self):
        """Computes a single player having two characters."""
        handler_mock = MagicMock()
        handler_mock.values().get.return_value = fake_cursor([
            ['FooBar#1234', '1', 'server', 'Alice', 'Hunter'],
            ['FooBar#1234', '1', 'server', 'Bob', 'Warrior'],
        ])

        spreadsheet = RosterSpreadsheet(handler_mock, '', '')
        players = await spreadsheet.get_players()

        self.assertEqual(len(players), 1)
        self.assertEqual(len(players[0].characters), 2)

    async def test_supports_multiple_players(self):
        """Computes two player, each having one character."""
        handler_mock = MagicMock()
        handler_mock.values().get.return_value = fake_cursor([
            ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
            ['Bar#4321', '2', 'server', 'Bob', 'Warrior'],
        ])

        spreadsheet = RosterSpreadsheet(handler_mock, '', '')
        players = await spreadsheet.get_players()

        self.assertEqual(len(players), 2)
        self.assertEqual(len(players[0].characters), 1)
        self.assertEqual(len(players[1].characters), 1)

    async def test_ignores_partial_data(self):
        """Computes a single player having two characters."""
        handler_mock = MagicMock()
        handler_mock.values().get.return_value = fake_cursor([
            ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
            ['Omega#1111', '', '', 'Bleh', 'Hunter'],
        ])

        spreadsheet = RosterSpreadsheet(handler_mock, '', '')
        players = await spreadsheet.get_players()

        self.assertEqual(len(players), 1)
        self.assertEqual(len(players[0].characters), 1)


if __name__ == '__main__':
    unittest.main()