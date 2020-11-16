"""Angular app building helper."""

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

import subprocess
import os

THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
WEB_DIRECTORY = os.path.join(THIS_DIRECTORY, '..', 'web')
if not os.path.exists(WEB_DIRECTORY):
    raise EnvironmentError(
        f'The directory "{WEB_DIRECTORY}" was not found. '
        'Code consistency issue?')


def _command_exists(command_name: str) -> bool:
    """Checks if a command exists in the environment."""
    check_cli = os.name == 'nt' and 'where' or 'which'
    result = subprocess.run(
        [check_cli, command_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    return result.returncode != 0


def build_angular(dev_mode: bool):
    """Builds the Angular application in dev/prod mode."""
    if _command_exists('npm'):
        raise EnvironmentError(
            'npm CLI was not found and is required to build '
            'an Angular application')
    if _command_exists('ng'):
        raise EnvironmentError(
            'ng CLI was not found and is required to build '
            'an Angular application.\n'
            'To install it, run npm install -g @angular/cli')

    # Build the angular application in dev/prod mode.
    args = [
        'ng', 'build', '--build-optimizer', '--aot']
    if not dev_mode:
        args.append('--prod')
    build = subprocess.run(args, cwd=WEB_DIRECTORY, shell=True)
    if build.returncode:
        raise RuntimeError(
            'Failed to build the Angular application. Check the above '
            'logs for further details.')
