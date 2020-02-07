from database.database import Database
from database.tables import EventsTable
from event.event import Event, StandardTimezone

from datetime import datetime
import logging

logging.getLogger().setLevel(logging.DEBUG)

db = Database()
table = EventsTable(db)

description = """Bring your flasks and consumables.

Also bring your happiness. And don't stand in tornadoes ffs."""
event = Event(
    "Mythic Raiding",
    StandardTimezone.europe.value.localize(datetime(2020, 2, 6, 20, 15)),
    description=description)
table.save(event)

table.save(Event(
    "Jesus' weird shit",
    StandardTimezone.europe.value.localize(datetime(2020, 2, 6, 23, 15)),
    description="""Yet another day where Jesus wants to do weird shit."""))

events = table.weekly()
print(events)
deserialized = events[0]
print(deserialized.date.astimezone(StandardTimezone.america.value))
