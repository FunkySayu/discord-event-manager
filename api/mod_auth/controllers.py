"""Controller utilities for authentication through Discord."""

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

from flask import Blueprint, request, session, redirect, url_for, jsonify

from config.discord import api_base_url, oauth2_client_secret
from api.mod_auth.session import make_session, get_discord_session, RequireAuthenticationError


mod_auth = Blueprint('auth', __name__, url_prefix='/auth')


@mod_auth.route('/discord/oauth')
def oauth_discord():
    """Redirects the user to the Discord authentication page."""
    discord = make_session()
    authorization_url, state = discord.authorization_url(
        f'{api_base_url}/oauth2/authorize')
    session['discord_oauth2_state'] = state
    return redirect(authorization_url)


@mod_auth.route('/discord/callback')
def callback():
    """Callback used when finalizing the authentication on Discord.
    This callback will redirect the user to the root of the application.
    """
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('discord_oauth2_state'))
    token = discord.fetch_token(
        f'{api_base_url}/oauth2/token',
        include_client_id=True,
        client_secret=oauth2_client_secret,
        authorization_response=request.url)
    session['discord_oauth2_token'] = token
    return redirect(url_for('root'))


@mod_auth.route('/discord/is_authenticated')
def check_authentication():
    """Returns a boolean indicating if the user is authenticated."""
    try:
        get_discord_session()
        return jsonify({'authenticated': True})
    except RequireAuthenticationError:
        return jsonify({'authenticated': False})


@mod_auth.route('/discord/logout')
def discord_logout():
    """Removes the discord tokens from the session."""
    session.pop('discord_oauth2_token')
    return redirect(url_for('root'))
