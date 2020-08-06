"""Controller utilities for accessing guild information."""

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

from flask import Blueprint, jsonify
from typing import Optional

from config.blizzard import get_wow_handler
from ui.base import db
from ui.mod_guild.guild import Region, WowGuild


def slugify(name: str) -> str:
    """Given a resource name (character, realm...) returns its slug name.

    The Blizzard API leverages resource names formatted in a specific way,
    where spaces are replaced by hyphens and all characters are lower cased.
    """
    return name.lower().replace(' ', '-')


mod_guild = Blueprint('wow', __name__, url_prefix='/api/guilds')


@mod_guild.route('/wow/<region>/<realm>/<name>')
def get_wow_guild(region: str, realm: str, name: str):
    try:
        region = Region(region)
    except ValueError:
        return jsonify({'error': 'Invalid region provided'}), 401

    guild: Optional[WowGuild] = WowGuild.query.filter_by(
        region=region, realm_slug=slugify(realm),
        name_slug=slugify(name)).one_or_none()
    # TODO(funkysayu): implement cache invalidation.
    if guild is None:
        guild = WowGuild.create_from_api(
            get_wow_handler(), region, slugify(realm), slugify(name))
        db.session.add(guild)
        db.session.commit()

    return jsonify(guild.to_dict())
