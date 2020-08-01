"""Wrapper around Google configuration variables."""

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

import codecs
import pickle
import logging

from config.base import config, save_generated_config, ConfigurationError
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

if 'google' not in config:
    raise ConfigurationError(
        'Section [google] is missing in the configuration.')

USER_SECTION, GENERATED_SECTION = 'google', 'generated.google'
if GENERATED_SECTION not in config:
    config.add_section(GENERATED_SECTION)

scopes = [
    scope.strip() for scope in
    config.get(USER_SECTION, 'scopes', fallback='').splitlines() if scope]


credentials = None


def save_credentials(new_credentials):
    """Saves the generated credential token in the configuration file."""
    config[GENERATED_SECTION]['auth_token'] = codecs.encode(
        pickle.dumps(new_credentials), "base64").decode()
    global credentials
    credentials = new_credentials
    save_generated_config()


_base64_credentials = config.get(GENERATED_SECTION, 'auth_token', fallback=None)
if _base64_credentials:
    try:
        credentials = pickle.loads(
            codecs.decode(_base64_credentials.encode(), "base64"))
    except (EOFError, pickle.UnpicklingError):
        # Simply assume the authentication token is null and move on.
        logging.warning(
                'An authentication token to Google server was provided but '
                'is invalid and cannot be used.')
        credentials = None

    # Sometimes tokens needs to be renewed. This is generally a one time,
    # fairly trivial operation and a one time. Make it happen at the
    # initialization.
    if credentials and not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            save_credentials(credentials)
        else:
            logging.error(
                'An authentication token to Google server was provided but '
                'is invalid and cannot be refreshed; Google integration is '
                'likely to have troubles.')

# The google sheets service handler.
_service = None


def get_sheets_handler():
    """Returns a unique service handler to Google services."""
    global _service
    if _service is not None:
        return _service

    if credentials is None:
        raise ConfigurationError(
            'Attempted to get a Google Sheets API handler without the '
            'appropriates API tokens. Use the script bin/generate_tokens.py '
            'to create the access tokens.')
    _service = build('sheets', 'v4', credentials=credentials)
    return _service