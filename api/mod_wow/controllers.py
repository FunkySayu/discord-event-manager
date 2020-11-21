"""Provides access to wow API data."""

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

from api.base import db
from api.mod_wow.character import WowCharacter
from api.mod_wow.realm import WowRealm
from api.mod_wow.region import Region
from config.blizzard import get_wow_handler

mod_wow = Blueprint('wow', __name__, url_prefix='/api/wow')


@mod_wow.route('/region')
def get_regions():
    """Returns the list of supported regions."""
    return jsonify(regions=[region.value for region in Region])


@mod_wow.route('/region/<region_str>/realm')
def get_realms(region_str: str):
    """Retrieves the list of all realms."""
    handler = get_wow_handler()
    try:
        region = Region(region_str.lower())
    except KeyError:
        return jsonify(error='Invalid region provided'), 400

    realms = WowRealm.load_realms_for_region(handler, region)
    for realm in realms:
        db.session.add(realm)
    db.session.commit()
    return jsonify(realms=[realm.to_dict() for realm in realms], region=region.value)


@mod_wow.route('/region/<region_str>/realm/<realm_slug>/character/<character_name>')
def get_character(region_str: str, realm_slug: str, character_name: str):
    """Retrieves a character information."""
    try:
        region = Region(region_str.lower())
    except KeyError:
        return jsonify(error='Invalid region provided'), 400

    handler = get_wow_handler()
    realm = WowRealm.get_or_create(handler, region, realm_slug)
    character = WowCharacter.get_or_create(handler, realm, character_name)
    return jsonify(character.to_dict())
