"""Provides direct/indirect interactions endpoints with the Blizzard API"""

from __future__ import annotations

__LICENSE__ = """
Copyright 2021 Google LLC
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
from api.base import db
from api.mod_auth.session import get_bnet_session, get_discord_session
from api.mod_wow.character import WowCharacter
from api.mod_wow.region import DEFAULT_REGION, Region
from api.mod_user.user import User, UserOwnsCharacters

mod_wow = Blueprint('wow', __name__, url_prefix='/api/wow')


@mod_wow.route('/me/characters')
def get_all_characters():
    """Returns all characters owned by the user, using Blizzard's API. """
    handler = get_wow_handler()
    bnet_session = get_bnet_session(DEFAULT_REGION)
    discord_session = get_discord_session()
    characters = WowCharacter.get_logged_user_characters(
        handler, bnet_session.token.get('access_token'), DEFAULT_REGION)
    
    # Create the relationship with the user, if not already existing.
    user = User.from_oauth_discord(discord_session)
    relationships = []
    for character in characters:
        existing = UserOwnsCharacters.query.filter_by(
            user_id=user.id, character_id=character.id).one_or_none()
        if existing is None:
            relationships.append(UserOwnsCharacters(user.id, character.id))
    
    # Save the characters in cache. This will reduce by a margin the
    # amount of QPS on the WoW API.
    db.session.add_all(relationships)
    db.session.add_all(characters)
    db.session.commit()
    return jsonify(data=[c.to_dict() for c in characters])

