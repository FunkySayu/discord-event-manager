"""Provides access to user data."""

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

from api.base import db
from config.blizzard import get_wow_handler
from api.mod_auth.session import get_discord_session
from api.mod_user.user import User, UserOwnsCharacters
from api.mod_user.forms import CharacterAssociationForm

mod_user = Blueprint('user', __name__, url_prefix='/api/user')


@mod_user.route('/')
def user():
    """Returns the Discord information about this user."""
    discord_session = get_discord_session()
    user = User.from_oauth_discord(discord_session)
    return jsonify(user.to_dict())


@mod_user.route('/<user_id>/characters', methods=['PUT', 'POST'])
def add_character(user_id: str):
    """Associates a character to the logged in user."""
    # TODO(funkysayu): Implement the visibility restriction.
    form = CharacterAssociationForm.from_json(request.get_json())
    if not form.validate():
        return jsonify(error='Invalid request', form_errors=form.errors), 400

    character = form.get_character(get_wow_handler())
    user = User.query.filter_by(id=user_id).one_or_none()
    if user is None:
        return jsonify(error='User not found'), 404

    relationship = UserOwnsCharacters(user.id, character.id)
    db.session.add(character)
    db.session.add(relationship)
    db.session.commit()

    return jsonify(character.to_dict())
