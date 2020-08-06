"""Wrapper around Flask configuration variables."""

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

# XXX: maybe refactor all this to create a flask Config object

import logging
import random
import string
import os

from config.base import config, ConfigurationError

if 'flask' not in config:
    raise ConfigurationError(
        'Section [flask] is missing in the configuration.')

USER_SECTION = 'flask'

debug = config.getboolean(USER_SECTION, 'debug', fallback=None)
if debug is None:
    logging.error(
        'Option debug in the section [flask] is unset; '
        'falling back to prod mode.')
    debug = False

port = config.getint(USER_SECTION, 'port', fallback=8080)

if debug:
    hostname = f'127.0.0.1:{port}'
elif 'hostname' in config[USER_SECTION]:
    hostname = config[USER_SECTION]['hostname']
else:
    logging.error(
        'Option hostname in the section [flask] is unset; '
        'falling back to the machine hostname, which may have side '
        'effects for production environments.')
    import socket
    hostname = f'{socket.gethostname()}:{port}'

# When running in debug mode, we use bare HTTP without SSL. Therefore
# some authentication OAuth2 authentication processes may fail for
# our own safety.
# Disable that safety for debug mode.
if debug and not os.environ.get('OAUTHLIB_INSECURE_TRANSPORT'):
    logging.warning(
        'Application is running in debug mode without disabling the SSL '
        'safety of OAuth2; overwriting this safety.')
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

secret_key = config.get(USER_SECTION, 'secret_key', fallback=None)
if secret_key is None:
    if not debug:
        raise ConfigurationError(
            'Secret option `secret_key` in the section [flask] is unset; '
            'this is required in production mode, as sessions are encoded '
            'in cookies that need to be cryptographically signed through '
            'this key.')
    logging.error(
        'Secret option `secret_key` in the section [flask] is unset; '
        'generating a random key for local development, but this option '
        'is required for production mode.')
    secret_key = "".join(random.choice(string.ascii_letters) for _ in range(10))

database_file = os.path.join(
    os.getcwd(),
    config.get(USER_SECTION, 'database_file', fallback='app.db'))
database_uri = f'sqlite:///{database_file}'
