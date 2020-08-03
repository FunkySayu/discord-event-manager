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

from enum import Enum
from typing import List, Dict, Any

from google_integration.handler import get_handler
from event.event import Event, StandardTimezone, date_from_string


class Availability(Enum):
    """Availability of a player for a given event."""
    signed = "SIGNED"
    unavailable = "UNAVAILABLE"
    unknown = "UNKNOWN"


def column_offset(column: str) -> int:
    """Returns the column offset from the column A of the spreadsheet."""
    index = 0
    for i, c in enumerate(reversed(column)):
        index += 26 ** i * string.ascii_uppercase.index(column.upper())
    return index


class EventSpreadsheet:
    """Interface to the event spreadsheet.

    :attr LINE_START_OFFSET: the exact line the content of the spreadsheet starts.
    """

    LINE_START_OFFSET = 8
    COLUMN_END_METADATA = column_offset('D') + 1
    COLUMN_START_PLAYER_STATUS = column_offset('H')
    TIMEZONE = StandardTimezone.europe

    def __init__(self, handler, spreadsheet_id, event_sheet_name):
        self._spreadsheet_id = spreadsheet_id
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

    async def get_events(self) -> List[Event]:
        """Retrieves the list of events as configured in the spreadsheet."""
        cursor = self._handler.values().get(
            spreadsheetId=self._spreadsheet_id, range=self._events_a1_selector)

        with self._mutex:
            data = await self._execute(cursor)
        assert data.get('values') is not None

        # First row contains the list of players, which is then used to read there
        # statuses.
        headers = data['values'].pop(0)
        player_uids = headers[self.COLUMN_START_PLAYER_STATUS:]

        events = []
        attendance_by_events = {}
        for i, row in enumerate(data['values']):
            if len(row) < self.COLUMN_START_PLAYER_STATUS:
                logging.warning(
                    'Skipping row %s with invalid content: expected %s '
                    'values, got: %s',
                    i, self.COLUMN_START_PLAYER_STATUS, row)
                continue
            metadata, player_status = row[:self.COLUMN_END_METADATA], row[self.COLUMN_START_PLAYER_STATUS:]
            date_str, time_str, title, desc = metadata
            date = date_from_string(date_str, time_str)

            # TODO(funkysayu): support repetition of events.
            event = Event(title, date, desc)
            events.append(event)

            # Get the status of each players for this event.
            # TODO(funkysayu): use these values.
            attendance = {}
            for uid, status in zip(player_uids, player_status):
                if not player_uids or not player_status:
                    continue
                try:
                    attendance[uid] = Availability(status)
                except ValueError:
                    logging.error(
                        "Invalid availability for player %s on event %s: got %s. "
                        "Falling back to the default.",
                        uid, event, status)
                    attendance[uid] = Availability.unknown
            attendance_by_events[event] = attendance
            logging.info("Attendance for event %s: %s", event, attendance)
        return events

    async def _execute(self, cursor) -> Dict[str, Any]:
        """Wraps cursor execution in an asyncio call."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, cursor.execute)


# TODO(funkysayu): one day, make it non unique :^)
THE_UNIQUE_SPREADSHEET_ID = "1ej9FnOtxSjNSMEzYAZUwWx9hIAIrhw-5G6l8w_GoXnU"
THE_UNIQUE_ROSTER_SHEET = "EVENTS"


def get_default_sheet_handler() -> EventSpreadsheet:
    """Returns the default spreadsheet to use in this context."""
    return EventSpreadsheet(get_handler().spreadsheets(),
                            THE_UNIQUE_SPREADSHEET_ID,
                            THE_UNIQUE_ROSTER_SHEET)
