"""Roster integration with Google Spreadsheet."""

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

import asyncio
import logging
import threading

from tabulate import tabulate
from typing import List, Dict, Any

from google_integration.handler import get_handler
from roster.model import Player, Character, CharacterClass


class RosterSpreadsheet:
    """Interface to the roster spreadsheet.

    :attr LINE_START_OFFSET: Exact line the content of the spreadsheet starts.
    :attr _spreadsheet_id: The spreadsheet ID to retrieve information from.
    :attr _roster_a1_selector: The sheet tab name to edit / pull data from.
    :attr _handler:
    """

    LINE_START_OFFSET = 3

    _spreadsheet_id: str
    _roster_a1_selector: str

    def __init__(self, handler, spreadsheet_id, roster_sheet_name):
        self._spreadsheet_id = spreadsheet_id
        self._roster_a1_selector = (
            f'{roster_sheet_name}!A{self.LINE_START_OFFSET}:F1000')
        self._handler = handler
        self._mutex = threading.Lock()

        # Google Spreadsheets API have two different notations to access a
        # specific sheet in a spreadsheet: using the A1 notation (for range
        # of values selection), the name of the spreadsheet needs to be used,
        # while some other endpoints may require the sheet ID (int32).
        # So we need to resolve what's the sheet ID associated to the sheet
        # name provided as argument.
        spreadsheet_metadata = self._handler.get(
            spreadsheetId=self._spreadsheet_id).execute()
        self._ROSTER_SHEET_ID = None
        for sheet_metadata in spreadsheet_metadata.get('sheets', []):
            if 'properties' not in sheet_metadata:
                continue
            properties = sheet_metadata['properties']
            if properties.get('title') != roster_sheet_name:
                continue
            self._ROSTER_SHEET_ID = properties.get('sheetId')
        if self._ROSTER_SHEET_ID is None:
            raise KeyError(
                'Sheet name {} is missing in the spreadsheet {}'.format(
                    roster_sheet_name, self._spreadsheet_id))

    async def get_players(self) -> List[Player]:
        """Retrieves the list of players as configured in the spreadsheet."""
        cursor = self._handler.values().get(
            spreadsheetId=self._spreadsheet_id,
            range=self._roster_a1_selector)

        with self._mutex:
            data = await self._execute(cursor)
        assert data.get('values') is not None

        player_by_uid = {}
        for row in data['values']:
            if len(row) < 5:
                # Incomplete inputs.
                continue
            [handle, uid, server, name, klass_name] = row
            if not (handle and uid and server and name and klass_name):
                # Incomplete inputs.
                continue
            if uid not in player_by_uid:
                player_by_uid[uid] = Player(handle, uid)
            player = player_by_uid[uid]
            player.characters.append(Character(
                server, name, CharacterClass(klass_name)))
        return list(player_by_uid.values())

    async def update_player(self, player: Player):
        """Updates the list of characters for the given player."""
        with self._mutex:
            cursor = self._handler.values().get(
                spreadsheetId=self._spreadsheet_id,
                range=self._roster_a1_selector)
            data = await self._execute(cursor)

            # Iterate in reverse order, so we can remove the rows without
            # having to deal with offsetting more and more the indexes.
            delete_requests = []
            for index, row in reversed(list(enumerate(data['values']))):
                if len(row) >= 2 and row[1] == player.discord_uuid:
                    # Delete any rows matching the user.
                    logging.debug(
                        'Deleting row %d (matching player %s)',
                        self.LINE_START_OFFSET+index,
                        player.discord_handle)
                    delete_requests.append({"deleteDimension": {"range": {
                            "sheetId": self._ROSTER_SHEET_ID,
                            "dimension": "ROWS",
                            "startIndex": self.LINE_START_OFFSET + index-1,
                            "endIndex": self.LINE_START_OFFSET + index,
                        },
                    }})

            if delete_requests:
                cursor = self._handler.batchUpdate(
                    spreadsheetId=self._spreadsheet_id,
                    body={'requests': delete_requests})
                await self._execute(cursor)

            # Now re-introduce the characters of the players, if any.
            if len(player.characters) < 1:
                return

            new_rows = []
            for character in player.characters:
                new_rows.append([
                    player.discord_handle,
                    player.discord_uuid,
                    character.server,
                    character.name,
                    character.klass.value,
                ])
            logging.debug(
                'Inserting the following %d rows: \n%s',
                len(new_rows),
                tabulate(new_rows))
            cursor = self._handler.values().append(
                spreadsheetId=self._spreadsheet_id,
                range=self._roster_a1_selector,
                valueInputOption="USER_ENTERED",
                body={'values': new_rows})
            await self._execute(cursor)

    async def _execute(self, cursor) -> Dict[str, Any]:
        """Wraps cursor execution in an asyncio call."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, cursor.execute)


# TODO(funkysayu): one day, make it non unique :^)
THE_UNIQUE_SPREADSHEET_ID = "1ej9FnOtxSjNSMEzYAZUwWx9hIAIrhw-5G6l8w_GoXnU"
THE_UNIQUE_ROSTER_SHEET = "ROSTER"


def get_default_sheet_handler():
    """Returns the default spreadsheet to use in this context."""
    return RosterSpreadsheet(get_handler().spreadsheets(),
                             THE_UNIQUE_SPREADSHEET_ID,
                             THE_UNIQUE_ROSTER_SHEET)
