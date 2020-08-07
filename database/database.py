"""Event storage logic."""

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

import tempfile

from abc import ABC, abstractmethod
from tinydb import TinyDB
from typing import TypeVar, NewType

from database.serializers import all_serializers

TableDef = TypeVar("TableDef")

# A database record
DbRecord = NewType("DbRecord", dict)


class Serializable(ABC):
    """Abstract representing an item serializable in database.

    A class implementing Serializable should be equal to itself when serialized
    and deserialized as in the following example:

    >>> class MyRecord(Serializable):
    ...     def __init__(self, id):
    ...         self.id = id
    ...     def serialize(self):
    ...         return {'id': self.id}
    ...     def deserialize(cls, record):
    ...         return cls(record.id)
    ...
    >>> r = MyRecord(1234)
    >>> assert r.id == MyRecord.deserialize(r.serialize()).id
    """

    @abstractmethod
    def serialize(self) -> DbRecord:
        """Serializes the class as a database record."""
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, record: DbRecord) -> Serializable:
        """Deserializes the database record into an instance of the class."""
        pass


class Database:
    """Database handler. General interface to all tables."""

    FILEPATH = tempfile.mkstemp()[1]

    def __init__(self):
        """Constructor."""
        self.db = TinyDB(self.FILEPATH, storage=all_serializers())

    def get_table(self, name: str):
        """Returns a table accessor on the database."""
        return self.db.table(name)
