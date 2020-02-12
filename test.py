from database.database import Database
from database.tables import EventsTable
from event.event import Event, StandardTimezone
from config.base import ConfigVariable, BaseConfig
from database.tables import ConfigsTable

from datetime import datetime
import logging

logging.getLogger().setLevel(logging.DEBUG)

db = Database()
table = EventsTable(db)

today = StandardTimezone.europe.value.localize(datetime.utcnow()).replace(
    hour=0, minute=0, second=0, microsecond=0)

description = """Bring your flasks and consumables.

Also bring your happiness. And don't stand in tornadoes ffs."""
event = Event(
    "Mythic Raiding",
    today.replace(hour=20, minute=45),
    description=description)
table.save(event)

# Ensure adding another event with the same date fails
try:
    table.save(Event(
        "Another event", today.replace(hour=20, minute=45), description="Foo"))
    raise AssertionError("Expected saving the same event twice to fail")
except ValueError:
    # We actually expect the save to raise a value error here.
    pass

table.save(Event(
    "Jesus' weird shit",
    today.replace(hour=23, minute=15),
    description="""Yet another day where Jesus wants to do weird shit."""))

events = table.weekly()
print(events)
deserialized = events[0]
print(deserialized.date.astimezone(StandardTimezone.america.value))

config_table = ConfigsTable(db)


class MyConfig(BaseConfig):
    CONFIGURATION_NAME = "testing"
    timezone = ConfigVariable(
        key="timezone",
        name="Default timezone used for this server.",
        description=(
            "This timezone will be used for any events created on the server. "
            "We provide timezones for the World of Warcraft servers in EU and "
            "NA, alternatively UTC."),
        values=list(StandardTimezone),
        default=StandardTimezone.america.name,
        constructor=StandardTimezone.from_string)


funkysayu = MyConfig(config_table, "FunkySayu")
assert funkysayu.timezone == StandardTimezone.america
funkysayu.timezone = StandardTimezone.europe
assert funkysayu.timezone == StandardTimezone.europe

another_funkysayu = MyConfig(config_table, "FunkySayu")
assert another_funkysayu.timezone == StandardTimezone.europe
