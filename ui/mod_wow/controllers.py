"""Controller utilities for accessing WoW informations."""

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
from flask import Blueprint, jsonify

from config.blizzard import get_handler


class WowRegions(Enum):
    """All valid wow regions, supported by the bot.

    We do not support China, as the whole endpoint mechanism would change.
    """
    eu = 'eu'
    na = 'na'

    @property
    def dynamic_namespace(self):
        """Returns the dynamic namespace for this region."""
        return f'dynamic-{self.value}'

    @property
    def static_namespace(self):
        """Returns the static namespace for this region."""
        return f'static-{self.value}'

    @property
    def profile_namespace(self):
        """Returns the profile namespace for this region."""
        return f'profile-{self.value}'


def slugify(name: str) -> str:
    """Given a resource name (character, realm...) returns its slug name.

    The Blizzard API leverages resource names formatted in a specific way,
    where spaces are replaced by hyphens and all characters are lower cased.
    """
    return name.lower().replace(' ', '-')


mod_wow = Blueprint('wow', __name__, url_prefix='/api/wow')


@mod_wow.route('/guilds/<region>/<server>/<name>')
def get_guild(region: str, server: str, name: str):
    try:
        region = WowRegions(region)
    except ValueError:
        return jsonify({'error': 'Invalid region provided'}), 401

    wow = get_handler()
    guild = wow.get_guild(
        region.value, region.profile_namespace,
        slugify(server), slugify(name))
    return jsonify(guild)
