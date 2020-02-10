from database.database import Database
from database.tables import EventsTable
from event.event import Event, StandardTimezone

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
