"""Controller utilities for accessing events information."""

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
from datetime import timedelta

from api.base import db
from api.mod_event.event import Event

mod_event = Blueprint('event', __name__, url_prefix='/api/events')

# The maximum amount of generation period possible when creating new events.
MAX_TIMEDELTA_EVENT_GENERATION = timedelta(weeks=4)


@mod_event.route('/')
def get_all_events():
    """Returns all events in the database."""
    # TODO(funkysayu): Implement the user visibility limit.
    events = Event.query.all()
    return jsonify(events=[e.to_dict() for e in events])


@mod_event.route('/<int:event_id>')
def get_event(event_id: int):
    """Returns one event."""
    # TODO(funkysayu): Implement the user visibility limit.
    event = Event.query.filter_by(id=event_id).one_or_none()
    if event is None:
        return jsonify(error='Event %r not found' % event_id), 404
    return jsonify(event.to_dict())


@mod_event.route('/<int:event_id>:next')
def get_next_event(event_id: int):
    """Returns the next event from the selected one.

    This route may fail if the event is not repeated, or if the event is
    too far ahead in time (to avoid over-generation of events).
    """
    # TODO(funkysayu): Implement the user visibility limit.

    # Check if we already created the event.
    maybe_created = Event.query.filter_by(parent_id=event_id).one_or_none()
    if maybe_created is not None:
        return jsonify(maybe_created.to_dict())

    event = Event.query.filter_by(id=event_id).one_or_none()
    if event is None:
        return jsonify(error='Event %r not found' % event_id), 404

    try:
        next_event = event.create_next_event()
    except ValueError:
        return jsonify(
            error='Cannot create the next occurrence of a non-repeated event.'), 412

    # Ensure we have an event generation limit.
    if next_event.date - event.date > MAX_TIMEDELTA_EVENT_GENERATION:
        return jsonify(
            error='Event is over the maximum generation period',
            max_period=MAX_TIMEDELTA_EVENT_GENERATION), 400

    db.session.add(next_event)
    db.session.commit()

    return jsonify(next_event.to_dict())
