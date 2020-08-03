"""Integration with Google Sheets, storing the events."""

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
import threading
import string
import logging

from typing import List, Dict, Any, Union

from config.google import get_sheets_handler
from event.event import Event, StandardTimezone, date_from_string
from event.attendance import Attendance, Availability
from roster.sheet_integration import RosterSpreadsheet, get_default_roster_sheet_handler
from roster.model import Player


def column_offset(column: str) -> int:
    """Returns the column offset from the column A of the spreadsheet."""
    index = 0
    for i, c in enumerate(reversed(column)):
        letter_offset = string.ascii_uppercase.index(c.upper())
        if i > 0:
            index += 26 ** i * (letter_offset + 1)
        else:
            index += string.ascii_uppercase.index(c.upper())
    return index


class EventSpreadsheet:
    """Interface to the event spreadsheet.

    :attr LINE_START_OFFSET: the exact line the content of the spreadsheet starts.
    """

    LINE_START_OFFSET = 8
    COLUMN_END_METADATA = column_offset('D') + 1
    COLUMN_START_PLAYER_STATUS = 'H'
    TIMEZONE = StandardTimezone.europe

    def __init__(self, handler, roster_sheet: RosterSpreadsheet, spreadsheet_id, event_sheet_name):
        self._spreadsheet_id = spreadsheet_id
        self._roster_sheet = roster_sheet
        self._sheet_name = event_sheet_name
        self._events_a1_selector = (
            f'{event_sheet_name}!A1:Z1000')
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
        self._EVENT_SHEET_ID = None
        for sheet_metadata in spreadsheet_metadata.get('sheets', []):
            if 'properties' not in sheet_metadata:
                continue
            properties = sheet_metadata['properties']
            if properties.get('title') != event_sheet_name:
                continue
            self._EVENT_SHEET_ID = properties.get('sheetId')
        if self._EVENT_SHEET_ID is None:
            raise KeyError(
                'Sheet name {} is missing in the spreadsheet {}'.format(
                    event_sheet_name, self._spreadsheet_id))

    async def get_all_attendances(self) -> List[Attendance]:
        """Retrieves the list of events as configured in the spreadsheet."""
        cursor = self._handler.values().get(
            spreadsheetId=self._spreadsheet_id, range=self._events_a1_selector)

        with self._mutex:
            data = await self._execute(cursor)
        assert data.get('values') is not None

        # First row contains the list of players, which is then used to read there
        # statuses.
        headers = data['values'].pop(0)
        player_offset = column_offset(self.COLUMN_START_PLAYER_STATUS)
        player_uids = await self._resolve_players(headers[player_offset:])

        attendances = []
        for i, row in enumerate(data['values']):
            if len(row) < self.COLUMN_END_METADATA:
                logging.warning(
                    'Skipping row %s with invalid content: expected %s '
                    'values, got: %s',
                    i, player_offset, row)
                continue
            metadata = row[:self.COLUMN_END_METADATA]
            player_status = []
            if len(row) >= player_offset:
                player_status = row[player_offset:]
            date_str, time_str, title, desc = metadata
            date = date_from_string(date_str, time_str)

            # TODO(funkysayu): support repetition of events.
            event = Event(title, date, desc)

            # Get the status of each players for this event.
            availabilities: Dict[Player, Availability] = {}
            for uid, status in zip(player_uids, player_status):
                if not player_uids or not player_status:
                    continue
                try:
                    availabilities[uid] = Availability(status)
                except ValueError:
                    logging.error(
                        "Invalid availability for player %s on event %s: got %s. "
                        "Falling back to the default.",
                        uid, event, status)
                    availabilities[uid] = Availability.unknown
            attendances.append(Attendance(event, availabilities))
            logging.info("Attendance for event %s: %s", event, availabilities)
        return attendances

    async def resync_player_list(self) -> List[str]:
        """Updates the list of available players in the event spreadsheet."""
        # TODO(funkysayu): it would be best to synchronize this once a player
        # is added in the roster, although it would imply creating a cycle
        # dependency from the RosterSpreadsheet to the EventSpreadsheet.
        # For now, stick to the simplest: adding a player will require a resync
        # in the event spreadsheet.
        all_players = await self._roster_sheet.get_players()

        # Only get the player headers, as we only care about the player list.
        a1_headers = f'{self._sheet_name}!{self.COLUMN_START_PLAYER_STATUS}1:AA1'
        cursor = self._handler.values().get(
            spreadsheetId=self._spreadsheet_id, range=a1_headers)
        with self._mutex:
            data = await self._execute(cursor)
            assert data.get('values') is not None

            registered_handles = data['values'][0]

            # We only want to add unregistered players, but not remove any players
            # missing in the roster. This would remove or offset all the data about
            # availability.
            players_to_add = set(player.discord_handle for player in all_players)
            for registered_handle in registered_handles:
                if registered_handle in players_to_add:
                    players_to_add.remove(registered_handle)

            cursor = self._handler.values().update(
                spreadsheetId=self._spreadsheet_id,
                range=a1_headers,
                valueInputOption="USER_ENTERED",
                body={
                    'values': [registered_handles + list(players_to_add)],
                })
            await self._execute(cursor)
            return list(players_to_add)

    async def _resolve_players(self, player_uids: List[str]) -> List[Union[Player, None]]:
        """Given a list of UIDs, get the player from the roster sheet."""
        all_players = await self._roster_sheet.get_players()
        by_uid = {player.discord_handle: player for player in all_players}
        return [by_uid.get(uid, None) for uid in player_uids]

    async def _execute(self, cursor) -> Dict[str, Any]:
        """Wraps cursor execution in an asyncio call."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, cursor.execute)


# TODO(funkysayu): one day, make it non unique :^)
THE_UNIQUE_SPREADSHEET_ID = "1ej9FnOtxSjNSMEzYAZUwWx9hIAIrhw-5G6l8w_GoXnU"
THE_UNIQUE_ROSTER_SHEET = "EVENTS"


def get_default_event_sheet_handler() -> EventSpreadsheet:
    """Returns the default spreadsheet to use in this context."""
    return EventSpreadsheet(get_sheets_handler().spreadsheets(),
                            get_default_roster_sheet_handler(),
                            THE_UNIQUE_SPREADSHEET_ID,
                            THE_UNIQUE_ROSTER_SHEET)
