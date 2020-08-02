"""Wrapper around Discord configuration variables."""

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

from config.base import config, ConfigurationError

if 'discord' not in config:
    raise ConfigurationError(
        'Section [discord] is missing in the configuration.')

USER_SECTION = 'discord'

api_base_url = config.get(USER_SECTION, 'api_base_url',
                          fallback='https://discordapp.com/api')

scopes = [
    scope.strip() for scope in
    config.get(USER_SECTION, 'scopes', fallback='').splitlines() if scope]


if 'oauth2_client_id' not in config[USER_SECTION]:
    raise ConfigurationError(
        'Missing OAuth2 client ID in the [discord] section. '
        'Ensure you made a copy of the secrets.sample.cfg file.')
if 'oauth2_client_secret' not in config[USER_SECTION]:
    raise ConfigurationError(
        'Missing OAuth2 client secret in the [discord] section. '
        'Ensure you made a copy of the secrets.sample.cfg file.')

oauth2_client_id = config[USER_SECTION]['oauth2_client_id']
oauth2_client_secret = config[USER_SECTION]['oauth2_client_secret']
