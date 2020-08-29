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

import logging

from enum import Enum
from datetime import datetime, timedelta
from flask_sqlalchemy import BaseQuery
from typing import Optional, Any
from pytz import utc, timezone, tzfile

from ui.base import db, BaseSerializerMixin
from ui.mod_guild.guild import Guild


class RepetitionFrequency(Enum):
    """Frequency at which an event should be repeated."""
    not_repeated = 'NOT_REPEATED'
    daily = 'DAILY'
    weekly = 'WEEKLY'

    @classmethod
    def _missing_(cls, value: Any) -> RepetitionFrequency:
        """Mark the event as not repeated if the value is missing."""
        logging.warning(
            'invalid frequency provided "%r"; falling back to unrepeated.',
            value)
        return cls.not_repeated

    def to_timedelta(self) -> Optional[timedelta]:
        """Returns the time delta from the repetition."""
        if self == RepetitionFrequency.not_repeated:
            return None
        if self == RepetitionFrequency.daily:
            return timedelta(days=1)
        if self == RepetitionFrequency.weekly:
            return timedelta(weeks=1)
        raise NotImplementedError(
            '%r does not have an associated timedelta.', self)


class Event(db.Model, BaseSerializerMixin):
    """An event bound to a guild, possibly repeated in time.

    Note the provided date MUST be associated to a timezone (aka aware date
    objects in the datetime documentation). This ensures the date is not
    open to interpretation when computing a timestamp, supporting the
    daylight saving times in some timezones.

    :attr title: Event title (e.g. Mythic Raiding)
    :attr description: Event description (e.g. Bring consumable, ...)
    :attr date: The date of the event.
    :attr repetition: A frequency at which the event should be repeated.
    """
    __tablename__ = 'event'

    # Automatically created by db.Model but clarifying existence for mypy.
    query: BaseQuery

    # Serialization options
    serialize_rules = (
        # Add the timezone informations
        'date', 'timezone_offset',
        # Remove internal representation of the date, which would be confusing
        '-_date_utc',
        # Remove circular dependency from the relationships
        '-guild', '-guild_id',
    )

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(
        db.DateTime,
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    parent_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    title = db.Column(db.String)
    description = db.Column(db.String)

    _date_utc = db.Column(db.DateTime)
    timezone_name = db.Column(db.String)
    repetition = db.Column(db.Enum(RepetitionFrequency))

    # Relationships
    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'))
    guild = db.relationship('Guild', uselist=False, back_populates='events')

    def __init__(self, guild: Guild,
                 title: str, date: datetime, description: str = "",
                 repetition=RepetitionFrequency.not_repeated,
                 parent: Event = None):
        self.guild = guild
        self.guild_id = guild.id

        self.title = title
        self.date = date
        self.description = description
        self.repetition = repetition
        if parent:
            self.parent_id = parent.id

    def __repr__(self):
        """Returns a debugging representation of the event."""
        return f'<Event "{self.title}" {self.date.isoformat()}>'

    @property
    def date(self):
        """Returns the date normalized on the original timezone."""
        if self._date_utc.tzinfo is None:
            self._date_utc = utc.localize(self._date_utc)
        return self.timezone.normalize(self._date_utc)

    @date.setter
    def date(self, date: datetime):
        """Updates the internal date of the model."""
        if date.tzinfo is None:
            raise ValueError(
                'The provided date is not associated with a timezone '
                'which may create side effects; associate a pytz.timezone.')
        if not hasattr(date.tzinfo, 'zone'):
            logging.warning(
                'The associated timezone data %r is not associated with a zone. '
                'The date will be normalized on UTC.')
            date = utc.normalize(date)
        self._date_utc = utc.normalize(date)
        self.timezone_name = date.tzinfo.zone

    @property
    def timezone(self) -> tzfile:
        """Returns the timezone name of the date."""
        return timezone(self.timezone_name)

    @property
    def timezone_offset(self) -> str:
        """Returns the timezone offset from UTC of the date."""
        return self.date.strftime('%z')

    def create_next_event(self) -> Event:
        """Returns the next event occurring after this one.

        Note the record is incomplete, i.e. the event has no ID until it is
        added to the database.

        For timezone adjustment (e.g. when the next event is on a different
        timezone than the original one because of daylight saving time),
        the original hour of the event remains stable.
        """
        if self.repetition is None:
            raise ValueError("Event %r is not repeated.", self)
        # As per datetime documentation, no time zone adjustments are done
        # even if the input is an aware object (i.e. has a timezone
        # associated). This operation will not modify the original hour of the
        # event.
        delta = self.repetition.to_timedelta()
        if delta is None:
            raise ValueError(
                "Cannot create the next event of a non-repeated event.")
        next_date = self.date + delta

        return Event(self.guild, self.title, next_date,
                     self.description, self.repetition, parent=self)
