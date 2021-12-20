"""Provides a wrapper around the WoW region system used in the API."""

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


class Region(Enum):
    """All supported regions."""
    eu = 'eu'
    us = 'us'

    # Blizzard namespaces conversion.
    # https://develop.battle.net/documentation/world-of-warcraft/guides/namespaces

    @property
    def dynamic_namespace(self):
        """Returns the Blizzard dynamic namespace for this region."""
        return f'dynamic-{self.value}'

    @property
    def static_namespace(self):
        """Returns the Blizzard static namespace for this region."""
        return f'static-{self.value}'

    @property
    def profile_namespace(self):
        """Returns the Blizzard profile namespace for this region."""
        return f'profile-{self.value}'


# The default region to use for little-region sensitive data.
DEFAULT_REGION = Region.eu
