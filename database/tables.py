"""Event storage logic."""

from __future__ import annotations

import logging

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from pytz import timezone

from event.event import Event, StandardTimezone
from database.database import Database, Query


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


def week_time_range(year: int, week: int,
                    tz: timezone) -> Tuple[datetime, datetime]:
    """Given a year and a week number, returns the time range corresponding.

    Note the returned end date matches exactly the start date of the next week
    (i.e. end date should be considered exclusive).
    """
    if not 1 <= week <= 52:
        raise IndexError("%s is not within the week range [1, 52]" % week)

    start = tz.localize(
        datetime.strptime(f"{year}-W{week - 1}-1", "%Y-W%W-%w"))
    return start, start + timedelta(days=7)


class EventsTable:
    """Interface to the event storage system.

    All accessors on this table will dynamically generate the next recuring
    events in the database based on the queried time range. For instance,

    All dates are stored in UTC for ease of manipulation. This becomes relevant
    whenever querying elements within a certain date range (e.g. weekly).
    """

    TABLE = "events"

    # Record shape, for hint only.
    RECORD = {
        'date': datetime,
        'title': str,
        'description': str,
        'repetition': bool,
        'parent': Optional[datetime],
    }

    def __init__(self, db: Database):
        """Constructor."""
        self.db = db

    def weekly(self, week: Optional[int] = None, year: Optional[int] = None,
               tz: StandardTimezone = StandardTimezone.utc) -> List[Event]:
        """Returns the list of event happening during the request week.

        If no specific week is requested, this will return the events happening
        during the current week.

        :param week: The week number to query (1 to 52). Defaults to the
                     current week.
        :param year: The year to query. Defaults to the current year.
        :param tz: Optional localization timezone to compute the current week
                   and year.
        """
        now = datetime.now()
        if not year:
            year = now.year
        if not week:
            week = now.isocalendar()[1]

        start, end = week_time_range(year, week, tz.value)
        events = self._list_events(start, end, generate=True)
        logging.debug("weekly: [%d, %d] -> [%s - %s]: %s",
                      year, week, start.isoformat(), end.isoformat(), events)
        return events

    def save(self, event: Event):
        """Saves an event in the table.

        In the case the event is repeated, it will verify if the parent have
        been stored in the database. If not, it will raise an exception.

        :param event: Event to be stored.
        """
        if event.parent is not None:
            if self.get(event.parent) is None:
                raise AttributeError(
                    "Event %s referes to an inexistent parent: %s" % (
                        repr(event), event.parent))
        self._save_record(event)

    # Table handlers.

    def get(self, date: datetime) -> Optional[Event]:
        """Retrieves an event by its date. Returns None if no event is found.

        :param date: an aware datetime object (with an associated timezone).
        """
        table = self.db.get_table(self.TABLE)
        query = Query()
        records = table.search(query.date == date)
        if len(records) > 1:
            raise ValueError(
                "Inconsistent database: got two records for the date %s" %
                date)
        if not records:
            return None
        return Event.deserialize(records[0])

    def _save_record(self, event: Event):
        """Actual logic saving the event in the table."""
        table = self.db.get_table(self.TABLE)
        table.insert(event.serialize())

    def _list_events(self, start: datetime, end: datetime,
                     generate: bool = False) -> List[Event]:
        """Returns the list of events within the provided time range."""
        table = self.db.get_table(self.TABLE)
        query = Query()
        records = table.search((query.date > start) & (end > query.date))
        return [Event.deserialize(e) for e in records]
