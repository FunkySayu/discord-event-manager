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

import unittest.mock

from datetime import datetime
from pytz import utc, timezone

from ui.common.testing import DatabaseTestFixture
from ui.mod_event.event import Event, RepetitionFrequency
from ui.mod_guild.guild import Guild


class TestEventModel(DatabaseTestFixture, unittest.TestCase):
    """Ensure consistency of the model."""

    def test_instantiation(self):
        """Tests a fairly basic instantiation works."""
        event = Event(
            Guild(12345),
            'Some title',
            datetime(2020, 10, 10, 10, 10, tzinfo=utc),
            'Some description')
        self.assertEqual(event.guild.id, 12345)
        self.assertEqual(event.title, 'Some title')
        self.assertEqual(event.date, datetime(2020, 10, 10, 10, 10, tzinfo=utc))
        self.assertEqual(event.description, 'Some description')

    def test_instantiation_fail_on_naive_datetime(self):
        """Ensures the provided date is associated to a timezone."""
        with self.assertRaises(ValueError):
            Event(
                Guild(12345),
                'Some title',
                datetime(2020, 10, 10, 10, 10),  # Missing timezone
                'Some description')

    def test_date_can_be_changed(self):
        """Tests the date can be changed on an event."""
        event = Event(
            Guild(12345),
            'Some title',
            datetime(2020, 10, 10, 10, 10, tzinfo=utc),
            'Some description')
        event.date = datetime(2020, 10, 10, 12, 10, tzinfo=utc)
        self.assertEqual(event.date, datetime(2020, 10, 10, 12, 10, tzinfo=utc))

    def test_date_change_fails_on_naive_datetime(self):
        """Ensures the changed date is associated to a timezone."""
        event = Event(
            Guild(12345),
            'Some title',
            datetime(2020, 10, 10, 10, 10, tzinfo=utc),
            'Some description')
        with self.assertRaises(ValueError):
            event.date = datetime(2020, 10, 10, 12, 10)

    def test_event_can_be_comitted(self):
        """Ensures consistency over a commit in the database."""
        event = Event(
            Guild(12345),
            'Some title',
            datetime(2020, 10, 10, 10, 10, tzinfo=timezone('Europe/Paris')),
            'Some description')

        self.db.session.add(event)
        self.db.session.commit()

        queried = Event.query.one()
        self.assertEqual(queried.guild.id, 12345)
        self.assertEqual(queried.title, 'Some title')
        self.assertEqual(
            queried.date,
            datetime(2020, 10, 10, 10, 10, tzinfo=timezone('Europe/Paris')))
        self.assertEqual(queried.timezone, timezone('Europe/Paris'))
        self.assertEqual(queried.timezone_name, 'Europe/Paris')

    def test_create_next_event_daily(self):
        """Checks if the daily generates the same event but a day later."""
        event = Event(
            Guild(12345),
            'Some title',
            datetime(2020, 10, 10, 10, 10, tzinfo=timezone('Europe/Paris')),
            'Some description',
            RepetitionFrequency.daily)

        next_event = event.create_next_event()

        self.assertEqual(next_event.guild.id, 12345)
        self.assertEqual(next_event.title, 'Some title')
        self.assertEqual(next_event.timezone, timezone('Europe/Paris'))
        self.assertNotEqual(next_event.date, event.date)
        self.assertEqual(
            next_event.date,
            datetime(2020, 10, 11, 10, 10, tzinfo=timezone('Europe/Paris')))

    def test_create_next_event_fails_if_not_repeated(self):
        """Checks if the daily generates the same event but a day later."""
        event = Event(
            Guild(12345),
            'Some title',
            datetime(2020, 10, 10, 10, 10, tzinfo=timezone('Europe/Paris')),
            'Some description')

        with self.assertRaises(ValueError):
            event.create_next_event()

    def test_all_repetition_frequency_have_timedelta(self):
        """Ensures we never raise NotImplementedError"""
        for value in RepetitionFrequency:
            if value is RepetitionFrequency.not_repeated:
                self.assertIsNone(value.to_timedelta())
            else:
                self.assertIsNotNone(value.to_timedelta())


if __name__ == '__main__':
    unittest.main()
