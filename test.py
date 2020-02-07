from database.database import Database
from database.tables import EventsTable
from event.event import Event, EUROPE

from datetime import datetime
import logging

logging.getLogger().setLevel(logging.DEBUG)

db = Database()
table = EventsTable(db)
event = Event("Mythic Raiding", datetime(2020, 2, 6, 20, 15, tzinfo=EUROPE))
table.save(event)
print(table.weekly())
