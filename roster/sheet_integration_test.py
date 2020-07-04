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

from roster.model import Player, Character, CharacterClass
from roster.sheet_integration import RosterSpreadsheet


class RosterSpreadsheetTest(unittest.IsolatedAsyncioTestCase):
    SHEET_METADATA = {'sheets': [{'properties': {'title': 'sheet name', 'sheetId': 133713371337}}]}

    def setUp(self):
        """Ensures we resolve the sheetId."""
        self.handler_mock = MagicMock()
        self.handler_mock.get().execute.return_value = self.SHEET_METADATA
        self.spreadsheet = RosterSpreadsheet(self.handler_mock, 'spreadsheetId', 'sheet name')

    async def test_supports_multiple_characters(self):
        """Computes a single player having two characters."""
        self.handler_mock.values().get().execute.return_value = {'values': [
            ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
            ['Foo#1234', '1', 'server', 'Bob', 'Warrior'],
        ]}

        players = await self.spreadsheet.get_players()

        self.assertEqual(len(players), 1)
        self.assertEqual(len(players[0].characters), 2)

    async def test_supports_multiple_players(self):
        """Computes two player, each having one character."""
        self.handler_mock.values().get().execute.return_value = {'values': [
            ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
            ['Bar#4321', '2', 'server', 'Bob', 'Warrior'],
        ]}

        players = await self.spreadsheet.get_players()

        self.assertEqual(len(players), 2)
        self.assertEqual(len(players[0].characters), 1)
        self.assertEqual(len(players[1].characters), 1)

    async def test_ignores_partial_data(self):
        """Computes a single player having two characters."""
        self.handler_mock.values().get().execute.return_value = {'values': [
            ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
            ['Omega#1111', '', '', 'Bleh', 'Hunter'],
        ]}

        print('test_ignores_partial_data')
        players = await self.spreadsheet.get_players()
        print(players)

        self.assertEqual(len(players), 1)
        self.assertEqual(len(players[0].characters), 1)

    async def test_update_deletes_previous_entries(self):
        """Computes a single player having two characters.

        An important part of this test is to ensure the deleted entries are in
        reverse order of the line number, as we do not want to deal with offsetting
        over our deletion.
        """
        self.handler_mock.values().get().execute.return_value = {'values': [
            ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
            ['Bar#1111', '2', 'server', 'Bob', 'Demon Hunter'],
            ['Foo#1234', '1', 'server', 'Richard', 'Demon Hunter'],
        ]}

        player = Player('Foo#1234', '1')
        await self.spreadsheet.update_player(player)

        self.handler_mock.batchUpdate.assert_called_with(
            spreadsheetId='spreadsheetId',
            body={
                'requests': [
                    {'deleteDimension': {'range': {
                        'sheetId': 133713371337,
                        'dimension': 'ROWS',
                        'startIndex': 4,  # Line offset + target - 1
                        'endIndex': 5  # Line offset + target
                    }}},
                    {'deleteDimension': {'range': {
                        'sheetId': 133713371337,
                        'dimension': 'ROWS',
                        'startIndex': 2,  # Line offset + target - 1
                        'endIndex': 3,  # Line offset + target
                    }}}
                ]
            })

    async def test_update_deletes_nothing_on_new_player(self):
        """Ensure we do not delete anything if we're adding a new player."""
        self.handler_mock.values().get().execute.return_value = {'values': [
            ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
            ['Bar#1111', '2', 'server', 'Bob', 'Demon Hunter'],
            ['Foo#1234', '1', 'server', 'Richard', 'Demon Hunter'],
        ]}

        player = Player('New#1234', '3')
        await self.spreadsheet.update_player(player)

        self.handler_mock.batchUpdate.assert_not_called()

    async def test_update_without_appends(self):
        """Ensure we do not try to add characters if the player don't own any."""
        self.handler_mock.values().get().execute.return_value = {'values': []}

        player = Player('New#1234', '3')
        await self.spreadsheet.update_player(player)

        self.handler_mock.values().append.assert_not_called()

    async def test_update_unregistered_player(self):
        """Insertion with a completely new player."""
        self.handler_mock.values().get().execute.return_value = {'values': [
            ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
        ]}

        player = Player('New#1234', '2', characters=[
            Character('server', 'Richard', CharacterClass.MAGE),
        ])
        await self.spreadsheet.update_player(player)

        self.handler_mock.batchUpdate.assert_not_called()
        self.handler_mock.values().append.assert_called_with(
            spreadsheetId="spreadsheetId",
            range="sheet name!A3:F1000",
            valueInputOption="USER_ENTERED",
            body={'values': [
                ['New#1234', '2', 'server', 'Richard', 'Mage']
            ]}
        )

    async def test_update_new_alt_player(self):
        """Insertion with a completely new player."""
        self.handler_mock.values().get().execute.return_value = {'values': [
            ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
            ['Bar#1111', '2', 'server', 'Bob', 'Demon Hunter'],
        ]}

        player = Player('Foo#1234', '1', characters=[
            Character('server', 'Alice', CharacterClass.HUNTER),
            Character('server', 'Richard', CharacterClass.MAGE),
        ])
        await self.spreadsheet.update_player(player)

        self.handler_mock.batchUpdate.assert_called_with(
            spreadsheetId='spreadsheetId',
            body={
                'requests': [
                    {'deleteDimension': {'range': {
                        'sheetId': 133713371337,
                        'dimension': 'ROWS',
                        'startIndex': 2,  # Line offset + target - 1
                        'endIndex': 3  # Line offset + target
                    }}},
                ]
            })
        self.handler_mock.values().append.assert_called_with(
            spreadsheetId="spreadsheetId",
            range="sheet name!A3:F1000",
            valueInputOption="USER_ENTERED",
            body={'values': [
                ['Foo#1234', '1', 'server', 'Alice', 'Hunter'],
                ['Foo#1234', '1', 'server', 'Richard', 'Mage']
            ]}
        )


if __name__ == '__main__':
    unittest.main()