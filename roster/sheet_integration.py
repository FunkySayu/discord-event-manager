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

from typing import List, Dict, Any

from google_integration.handler import get_handler
from roster.model import Player, Character, CharacterClass


class RosterSpreadsheet:
    """Interface to the roster spreadsheet.

    :attr _SPREADSHEET_ID: The Google spreadsheet ID to retrieve information from.
    :attr _ROSTER_SHEET: The Spreadsheet tab to edit / pull data from.
    """

    _SPREADSHEET_ID: string
    _ROSTER_SHEET: string

    def __init__(self, handler, spreadsheet_id, roster_sheet):
        self._SPREADSHEET_ID = spreadsheet_id
        self._ROSTER_SHEET = roster_sheet
        self._handler = handler

    async def get_players(self) -> List[Player]:
        """Retrieves the list of players as configured in the spreadsheet."""
        cursor = self._handler.values().get(spreadsheetId=self._SPREADSHEET_ID,
                                            range=f"{self._ROSTER_SHEET}!A3:F1000")
        data = await self._execute(cursor)
        assert data.get('values') is not None
        assert all(len(columns) == 5 for columns in data['values'])

        player_by_uid = {}
        for [handle, uid, server, name, klass_name] in data['values']:
            if not (handle and uid and server and name and klass_name):
                # Incomplete inputs.
                continue
            if uid not in player_by_uid:
                player_by_uid[uid] = Player(handle, uid)
            player = player_by_uid[uid]
            player.characters.append(Character(server, name, CharacterClass(klass_name)))
        return list(player_by_uid.values())

    async def _execute(self, cursor) -> Dict[string, Any]:
        """Wraps cursor execution in an asyncio call."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, cursor.execute)


# TODO(funkysayu): one day, make it non unique :^)
THE_UNIQUE_SPREADSHEET_ID = "1ej9FnOtxSjNSMEzYAZUwWx9hIAIrhw-5G6l8w_GoXnU"
THE_UNIQUE_ROSTER_SHEET = "ROSTER"


def get_default_sheet_handler():
    """Returns the default spreadsheet to use in this context."""
    return RosterSpreadsheet(get_handler().spreadsheets(), THE_UNIQUE_SPREADSHEET_ID, THE_UNIQUE_ROSTER_SHEET)