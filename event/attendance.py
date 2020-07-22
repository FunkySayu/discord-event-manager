"""Attendance records for a given event."""

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

from enum import Enum
from typing import Dict

from event.event import Event
from roster.model import Player

class Availability(Enum):
    """Availability of a player for a given event."""
    signed = "SIGNED"
    unavailable = "UNAVAILABLE"
    unknown = "UNKNOWN"

    def __repr__(self):
        return '<Availability {}>'.format(self.value)


class Attendance:
    """Player attendance to an event."""
    event: Event
    availabilities: Dict[Player, Availability]

    def __init__(self, event: Event, availabilities: Dict[Player, Availability] = None):
        self.event = event
        self.availabilities = availabilities or {}

