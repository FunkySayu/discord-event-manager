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

from flask import Blueprint, jsonify, request
from typing import Optional

from config.blizzard import get_wow_handler
from ui.base import db
from ui.mod_event.event import Event
from ui.mod_guild.guild import Guild, Region, WowGuild
from ui.mod_guild.forms import EventCreationForm


def slugify(name: str) -> str:
    """Given a resource name (character, realm...) returns its slug name.

    The Blizzard API leverages resource names formatted in a specific way,
    where spaces are replaced by hyphens and all characters are lower cased.
    """
    return name.lower().replace(' ', '-')


mod_guild = Blueprint('guild', __name__, url_prefix='/api/guilds')


@mod_guild.route('/')
def get_all_guilds():
    """Returns all the guilds the user can see. Events are not returned.

    A guild is visible to the user if:
     - the user is its Discord owner
     - the bot is present in the guild as well as himself.

    Events are not returned from this route to lower the size of the response.
    """
    # TODO(funkysayu): Implement the visibility limit.
    guilds = Guild.query.all()
    return jsonify(guilds=[g.to_dict(rules=('-events',)) for g in guilds])


@mod_guild.route('/<str:guild_id>')
def get_one_guild(guild_id: int):
    """Returns a guild from its ID as well as its associated events."""
    # TODO(funkysayu): Implement the visibility limit.
    guild = Guild.query.filter_by(id=guild_id).one_or_none()
    if guild is None:
        return jsonify(error="Guild %s does not exist." % guild_id), 404
    return jsonify(guild.to_dict())


@mod_guild.route('/<str:guild_id>/events')
def get_guild_events(guild_id: int):
    """Returns the events scheduled for this guild."""
    # TODO(funkysayu): Implement the user visibility limit.
    events = Event.query.filter_by(guild_id=guild_id).all()
    return jsonify(events=[e.to_dict() for e in events])


@mod_guild.route('/<str:guild_id>/events', methods=['PUT'])
def create_guild_event(guild_id: int):
    """Creates an event for this guild."""
    # TODO(funkysayu): Implement the visibility limit.
    form = EventCreationForm.from_json(request.get_json())
    if not form.validate():
        return jsonify(error='Invalid request', form_errors=form.errors), 400
    guild = Guild.query.filter_by(id=guild_id).one_or_none()
    if guild is None:
        return jsonify(error='Guild %r does not exist' % guild_id), 404
    event = form.convert_to_event(guild)
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict())


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
