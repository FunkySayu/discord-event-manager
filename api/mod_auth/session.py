"""Session utilities on Discord."""

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

from flask import session, jsonify
from requests_oauthlib import OAuth2Session
from datetime import datetime

from config.discord import api_base_url, oauth2_client_id, oauth2_client_secret, scopes
from config.blizzard import client_id, client_secret
from config.flask import hostname
from werkzeug.exceptions import HTTPException
from api.mod_wow.region import Region

OAUTH2_REDIRECT_URI = f'http://{hostname}/auth/discord/callback'
OAUTH2_BNET_REDIRECT_URI = f'http://{hostname}/auth/bnet/callback'

class RequireAuthenticationError(HTTPException):
    """User attempted an action that requires a missing authentication."""
    code = 401
    description = 'Cannot perform that action without an authentication.'


def _discord_token_updater(token):
    """Callback registering an user OAuth2 token in its session."""
    session['discord_oauth2_token'] = token


def make_session(token=None, state=None) -> OAuth2Session:
    """Creates a OAuth2 session object from one of the 3 provided objects."""
    return OAuth2Session(
        client_id=oauth2_client_id,
        token=token or session.get('discord_oauth2_token'),
        state=state or session.get('discord_oauth2_state'),
        scope=scopes,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': oauth2_client_id,
            'client_secret': oauth2_client_secret,
        },
        auto_refresh_url=f'{api_base_url}/oauth2/token',
        token_updater=_discord_token_updater)

def get_discord_session() -> OAuth2Session:
    """Returns the current session or raise an exception.
    Wrapper around make_session to quickly access the session or fail
    if the user did not do the authentication process.
    """
    token = session.get('discord_oauth2_token')
    if token is None:
        raise RequireAuthenticationError()
    return make_session(token=token)


def _bnet_token_updater(token):
    """Callback registering an user OAuth2 token in its session."""
    session['bnet_oauth2_token'] = token


def make_bnet_session(region: Region, token=None, state=None) -> OAuth2Session:
    """Creates a OAuth2 session object from one of the 3 provided objects."""
    return OAuth2Session(
        client_id=client_id,
        token=token or session.get('bnet_oauth2_token'),
        state=state or session.get('bnet_oauth2_state'),
        scope=['wow.profile'],
        redirect_uri=OAUTH2_BNET_REDIRECT_URI,
        token_updater=_bnet_token_updater)


def get_bnet_session(region: Region) -> OAuth2Session:
    """Returns the current session or raise an exception.
    
    Wrapper around make_session to quickly access the session or fail
    if the user did not do the authentication process.
    """
    token = session.get('bnet_oauth2_token')
    if token is None or token['expires_at'] < datetime.timestamp(datetime.now()):
        session['bnet_oauth2_token'] = None
        session['bnet_oauth2_state'] = None
        raise RequireAuthenticationError()
    return make_bnet_session(region, token=token)
