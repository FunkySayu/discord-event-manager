"""Definition of an event."""

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

import dateutil.parser

from datetime import datetime, timedelta
from enum import Enum
from pytz import timezone
from typing import Optional, List

from database.database import DbRecord, Serializable


class StandardTimezone(Enum):
    """A list of supported timezones for the server."""
    utc = timezone("UTC")
    europe = timezone("Europe/Paris")
    america = timezone("America/Los_angeles")

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_string(cls, string: str) -> StandardTimezone:
        try:
            return cls[string]
        except KeyError:
            raise ValueError("Timezone %s is not supported." % string)


def date_from_string(date_str: str, time_str: str, tz = StandardTimezone.utc):
    """Creates an aware datetime object from a date and time string."""
    unaware_date = dateutil.parser.parse(f'{date_str} {time_str}')
    return tz.value.localize(unaware_date)


class Event(Serializable):
    """An event, possibly repeated in time.

    Note the provided date MUST be associated to a timezone (aka aware date
    objects in the datetime documentation). This ensures the date is not
    open to interpretation when computing a timestamp, supporting the
    daylight saving times in some timezones.

    Usage example:
    >>> from datetime import datetime, timedelta
    >>> import pytz
    >>> event = Event("Mythic Raiding",
    ...     datetime(2019, 6, 20, 20, 30, 0, 0, pytz.timezone("Europe/Paris")),
    ...     repetition=timedelta(days=7))
    <Event "Mythicc Raiding" 2019-06-20T20:30:00+00:00>
    >>> event.next()
    <Event "Mythicc Raiding" 2019-06-27T20:30:00+00:00>


    :attr title:        Event title (e.g. Mythic Raiding)
    :attr description:  Event description (e.g. Bring consumable, ...)
    :attr date:         The date of the event. In the case of a repeated event,
                        the initial date of the event.
    :attr repetition:   A timedelta providing the repetition period.
    :attr parent:       If the event is repeated, parent is the very first
                        event created.
    """
    title: str
    date: datetime
    description: str
    repetition: Optional[timedelta]
    parent: Optional[datetime]

    def __init__(self, title: str, date: datetime, description: str = "",
                 repetition: Optional[timedelta] = None,
                 parent: Optional[datetime] = None):
        if date.tzinfo is None:
            raise ValueError(
                "The provided date is not associated with a timezone "
                "which may create side effects; associate a pytz.timezone.")
        self.title = title
        self.date = date
        self.description = description
        self.repetition = repetition
        self.parent = parent

    def __repr__(self):
        """Returns a debugging representation of the event."""
        return f'<Event "{self.title}" {self.date.isoformat()}>'

    def serialize(self) -> DbRecord:
        """Serializes the event into a database record."""
        data = {
            'date': self.date,
            'title': self.title,
            'description': self.description,
            'repetition': self.repetition,
        }
        if self.parent:
            data.parent = data.parent.date.isoformat()
        return data

    @classmethod
    def deserialize(cls, dbrecord: DbRecord) -> Event:
        """Deserializes the database record into an event."""
        return cls(
            dbrecord.get('title'),
            dbrecord.get('date'),
            dbrecord.get('description'),
            dbrecord.get('repetition'),
            dbrecord.get('parent'))

    def next(self) -> Event:
        """Returns the next event occurring after this one.

        Note that on timezone adjustement (e.g. daylight saving time) the
        original hour of the event remains stable.
        """
        if self.repetition is None:
            raise ValueError(
                "Attempted to get the next event from a non-recurring event.")
        # As per datetime documentation, no time zone adjustments are done
        # even if the input is an aware object (i.e. has a timezone
        # associated). This operation will not modify the original hour of the
        # event.
        next_date = self.date + self.repetition

        # Ensure the parent is stable within all the events.
        parent = None
        if self.parent is not None:
            parent = self.parent.date

        return Event(self.title, next_date, self.description, self.repetition,
                     parent)

    def all_within(self, start: datetime, end: datetime) -> List[Event]:
        """Returns all occurences of the event within the provided timerange.

        If the event is not recuring, returns either a list of itself if the
        event is happening within the provided range or an empty list.
        """
        if self.repetition is None:
            if start <= self.date <= end:
                return [self]
            return []

        result, current = [], self
        while current.date <= end:
            if start <= current.date:
                result.append(start)
            current = current.next()
        return result