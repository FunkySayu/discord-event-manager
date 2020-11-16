"""Implements simple commands interacting with the event database."""

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

import argparse
import discord
import shlex
import sys

from datetime import datetime, timedelta
from typing import Tuple
from pytz import UTC, timezone, UnknownTimeZoneError

from api.base import app
from api.mod_event.event import Event
from bot.handlers.base import CommandHandler


DEFAULT_TIMEZONE = UTC


class ArgumentParser(argparse.ArgumentParser):
    def _get_action_from_name(self, name):
        """Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is
        passed as it's first arg...
        """
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        super(ArgumentParser, self).error(message)


class CommandWeekly(CommandHandler):
    """Lists the events happening this week."""

    COMMAND = 'weekly'
    DAY_FORMAT, TIME_FORMAT = "%a %d %b", "%H:%M (%Z)"

    async def handle(self, message: discord.Message):
        """Lists the events happening this week."""
        now = datetime.now()
        year = now.year
        week = now.isocalendar()[1]
        start, end = CommandWeekly.week_time_range(year, week, DEFAULT_TIMEZONE)
        # TODO(funkysayu): Implement visibility restriction when listing events.
        with app.app_context():
            results = Event.query.filter(
                Event.date >= start,
                Event.date < end).all()
        events = [self.format_event(event) for event in results]
        if not events:
            await message.channel.send('No events this week!')
        else:
            await message.channel.send("\n\n".join(events))

    def format_event(self, event: Event) -> str:
        """Formats an event to send it in a Discord message."""
        date = event.date.astimezone(DEFAULT_TIMEZONE)
        text = "%s %s: **%s**" % (date.strftime(self.DAY_FORMAT),
                                  date.strftime(self.TIME_FORMAT), event.title)
        if event.description is not None:
            text += "\n" + "\n".join(
                "> %s" % line for line in event.description.splitlines())
        return text

    @staticmethod
    def week_time_range(year: int, week: int,
                        tz: datetime.tzinfo) -> Tuple[datetime, datetime]:
        """Given a year and a week number, returns the time range corresponding.

        Note the returned end date matches exactly the start date of the next week
        (i.e. end date should be considered exclusive).
        """
        if not 1 <= week <= 52:
            raise IndexError("%s is not within the week range [1, 52]" % week)

        start = tz.localize(
            datetime.strptime(f"{year}-W{week - 1}-1", "%Y-W%W-%w"))
        return start, start + timedelta(days=7)


class CommandSetTimezone(CommandHandler):
    """Sets the timezone for all events managed by this server."""

    COMMAND = 'set_timezone'

    async def handle(self, message: discord.Message):
        """Sets the timezone for all events managed by this server."""
        # TODO(funkysayu): actually make it server dependent
        parser = ArgumentParser()
        parser.add_argument('timezone')
        try:
            args = parser.parse_args(shlex.split(message.content)[1:])
        except argparse.ArgumentError as exc:
            await message.channel.send("Failed: " + exc.message)
            return

        try:
            tzinfo = timezone(args.timezone)
        except UnknownTimeZoneError:
            await message.channel.send(
                f'Failed: unknown timezone "{args.timezone}"')
            return

        global DEFAULT_TIMEZONE
        DEFAULT_TIMEZONE = tzinfo
        await message.channel.send("Done: timezone was modified to %s (%s)" % (
            DEFAULT_TIMEZONE.zone,
            datetime.now().astimezone(DEFAULT_TIMEZONE).strftime("UTC%z")))
