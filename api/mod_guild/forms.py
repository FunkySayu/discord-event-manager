"""Forms validating data sent by the user."""

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


from pytz import utc, timezone
from wtforms import Form, DateTimeField, StringField, validators

from api.common.forms import EnumField
from api.mod_guild.guild import Guild
from api.mod_event.event import Event, EventRepetitionFrequency


class EventCreationForm(Form):
    """Field checker for creating an event."""
    title = StringField('Title', [
        validators.DataRequired(),
        validators.Length(min=4, max=32),
    ])
    description = StringField('Description', [validators.Length(max=2000)])
    date = DateTimeField('Date')
    repetition = EnumField('Repetition frequency', enum=EventRepetitionFrequency,
                           default=EventRepetitionFrequency.not_repeated.value)
    timezone_name = StringField('Forced timezone')

    def convert_to_event(self, guild: Guild) -> Event:
        """Converts the data provided in the form to an event."""
        # TODO(funkysayu): Once we create the complete setup phase, where a
        #   Guild is associated to a WowGuild which itself is associated to
        #   a realm-wise timezone, use this timezone as the default one.
        #   For now and as long as we don't have this link, default to UTC.
        tz = utc
        if self.timezone_name.data:
            tz = timezone(self.timezone_name.data)
        date = tz.localize(self.date.data)
        return Event(
            guild, self.title.data, date,
            self.description.data, self.repetition.data)
