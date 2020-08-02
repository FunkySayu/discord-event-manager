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

from flask import Blueprint, jsonify

from config.discord import api_base_url
from ui.mod_auth.session import get_discord_session

mod_user = Blueprint('user', __name__, url_prefix='/api/user')


@mod_user.route('/')
def user():
    """Returns the Discord information about this user."""
    discord = get_discord_session()
    user = discord.get(api_base_url + '/users/@me').json()
    guilds = discord.get(api_base_url + '/users/@me/guilds').json()
    return jsonify(user=user, guilds=guilds)
