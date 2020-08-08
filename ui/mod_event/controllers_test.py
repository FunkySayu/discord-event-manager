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

import unittest

from datetime import datetime
from pytz import utc

from ui.common.testing import ControllerTestFixture
from ui.mod_event.controllers import mod_event
from ui.mod_event.event import Event, RepetitionFrequency
from ui.mod_guild.guild import Guild


class TestEventControllers(ControllerTestFixture, unittest.TestCase):

    BLUEPRINTS = [mod_event]

    def setUp(self):
        """Add some stuff in the database."""
        super().setUp()

        guild = Guild(12345)
        self.db.session.add(guild)
        self.db.session.add(Event(
            guild, 'One',
            datetime(2020, 10, 10, 10, 0, tzinfo=utc)))
        self.db.session.add(Event(
            guild, 'Two',
            datetime(2020, 10, 10, 11, 0, tzinfo=utc),
            repetition=RepetitionFrequency.weekly))
        self.db.session.commit()

    def test_get_all_events(self):
        """Ensure we return all events in the database."""
        with self.client as client:
            results = client.get('/api/events/')

        events = results.json.get('events')
        self.assertEqual(len(results.json.get('events')), 2)
        self.assertEqual(set(e.get('id') for e in events), {1, 2})

    def test_get_event(self):
        """Ensure we can retrieve a single event with its basic info."""
        with self.client as client:
            results = client.get('/api/events/1')

        self.assertEqual(results.json['id'], 1)
        self.assertEqual(results.json['title'], 'One')
        self.assertEqual(results.json['date'], '2020-10-10 10:00')
        self.assertEqual(results.json['timezone_name'], 'UTC')
        self.assertEqual(results.json['timezone_offset'], '+0000')

    def test_get_next_event(self):
        """Ensure we can get the next event, if repeated."""
        with self.client as client:
            results = client.get('/api/events/2:next')

        self.assertEqual(results.json['title'], 'Two')
        self.assertEqual(results.json['date'], '2020-10-17 11:00')
        self.assertEqual(results.json['timezone_name'], 'UTC')
        self.assertEqual(results.json['timezone_offset'], '+0000')

    def test_get_next_event_do_not_generate_twice_the_event(self):
        """Ensure we do not generate two different events from one."""
        with self.client as client:
            first = client.get('/api/events/2:next')
            second = client.get('/api/events/2:next')

        self.assertEqual(first.json['id'], second.json['id'])

    def test_get_next_event_has_a_limit(self):
        """Ensure at some points, we limit the event generation."""
        with self.client as client:
            event_id = 2
            for tries in range(10):
                results = client.get(f'/api/events/{event_id}:next')
                if results.status != 200:
                    break
                event_id = results.json['id']
            else:
                self.fail('Event were still generated after 10 tries.')
