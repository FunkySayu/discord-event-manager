"""Additional custom serializers, supporting custom types in TinyDB.

TinyDB does not support all types by default, but having customized types
supported "natively" in the database becomes quite handy when these types are
repeated over and over (for instance, datetime objects). This file defines
additional serializers able to encode such objects.
"""

from __future__ import annotations
import dateutil.parser
import logging

from datetime import datetime
from tinydb_serialization import SerializationMiddleware, Serializer


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


class DateTimeSerializer(Serializer):
    """Allows to natively serialize datetime objects in TinyDB.

    If the serialized datetime is an aware object, the deserialized datetime is
    ensured to be associated to the appropriate timezone.
    """

    # Required by Serializer to know what to encode.
    OBJ_CLASS = datetime
    # ISO 8601 compliant format encoded in the database.
    ISO8601_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"

    def encode(self, date: datetime) -> str:
        """Encodes a date, using the ISO 8601 notation."""
        logging.debug('encoded date: %s -> %s', date, date.strftime(self.ISO8601_FORMAT))
        return date.strftime(self.ISO8601_FORMAT)

    def decode(self, string: str) -> datetime:
        """Decodes a date from its ISO 8601 notation."""
        date = dateutil.parser.isoparse(string)
        logging.debug('decoded date: %s -> %s', string, date.strftime(self.ISO8601_FORMAT))
        return date


def all_serializers() -> SerializationMiddleware:
    """Registers all serializers in a single middleware to attach to the DB."""
    middleware = SerializationMiddleware()
    middleware.register_serializer(DateTimeSerializer(), 'TinyDate')
    return middleware
