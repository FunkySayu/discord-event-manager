"""Wrapper around Blizzard configuration variables."""

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

from wowapi import WowApi

from config.base import config, ConfigurationError

if 'blizzard' not in config:
    raise ConfigurationError(
        'Section [blizzard] is missing in the configuration.')

USER_SECTION = 'blizzard'


if 'client_id' not in config[USER_SECTION]:
    raise ConfigurationError(
        'Missing OAuth2 client ID in the [blizzard] section. '
        'Ensure you made a copy of the secrets.sample.cfg file.')
if 'client_secret' not in config[USER_SECTION]:
    raise ConfigurationError(
        'Missing OAuth2 client secret in the [blizzard] section. '
        'Ensure you made a copy of the secrets.sample.cfg file.')

client_id = config[USER_SECTION]['client_id']
client_secret = config[USER_SECTION]['client_secret']

_service = None


def get_handler() -> WowApi:
    """Returns a configured handler to reach the Blizzard API."""
    global _service
    if _service is not None:
        return _service

    _service = WowApi(client_id, client_secret)
    return _service
