"""Utilities to manage forms in the backend."""

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
from typing import Type

from wtforms import SelectField


class EnumField(SelectField):
    """Form field checking the sent data against the values of an Enum."""

    def __init__(self, *args, enum: Type[Enum], **kwargs):
        self.enum = enum
        kwargs['choices'] = self._choices()
        kwargs['coerce'] = self._coerce
        super().__init__(*args, **kwargs)

    def _choices(self):
        """Returns the list of possible values of the enum."""
        return [(choice, choice.name) for choice in self.enum]

    def _coerce(self, item):
        """Converts the value to its enum."""
        return item if isinstance(item, self.enum) else self.enum(item)
