"""Simple wrapper around the core configuration file.

Bot configuration is split in two parts: the user configuration and the
generated tokens. This file offers an API to read from both file and save
generated content easily.

We never want to change the user configuration, as not only it will remove any
comments but it is also a source of truth and should be considered immutable.
"""

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

import configparser
import os


class ConfigurationError(ValueError):
    """Raised when the configuration is inconsistent with its usage."""


USER_CONFIGURATION_FILE = 'config.cfg'
GENERATED_CONFIGURATION_FILE = 'generated.cfg'

if not os.path.exists(USER_CONFIGURATION_FILE):
    raise ConfigurationError(f'Configuration file not found: {USER_CONFIGURATION_FILE}')

config = configparser.ConfigParser()


def save_generated_config():
    """Saves the generated parts of the configuration in the generated.cfg file.

    Generated sections are prefixed by `generated.`. All their content will be
    copied in the new generated.cfg file. Other content (i.e. user configuration)
    will be ignored.
    """
    new_generated = configparser.ConfigParser()
    for section in config.sections():
        if not section.startswith('generated.'):
            continue
        new_generated.add_section(section)
        for key in config[section].keys():
            new_generated[section][key] = config[section][key]

    with open(GENERATED_CONFIGURATION_FILE, 'w') as f:
        new_generated.write(f)


# Read the generated configuration first (if any) and let the
# user defined one overwrite its data.
if os.path.exists(GENERATED_CONFIGURATION_FILE):
    config.read(GENERATED_CONFIGURATION_FILE)
config.read(USER_CONFIGURATION_FILE)
