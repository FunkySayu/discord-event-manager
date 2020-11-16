"""Preloads World of Warcraft static and dynamic data."""

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

import argparse
import logging
import os

from tqdm import tqdm
from typing import Tuple, List

from config.blizzard import get_wow_handler
from config.flask import database_file
from ui.app import app, db
from ui.mod_wow.region import Region
from ui.mod_wow.realm import WowRealm


parser = argparse.ArgumentParser(
    description='Database preloader')
parser.add_argument(
    '--recreate_database', dest='recreate_database', action='store_true',
    help='if present, removes the previous database file')


def preload_realms():
    """Lists all realms available and preload them in database."""
    handler = get_wow_handler()
    realms: List[Tuple[Region, str]] = []

    for region in Region:
        index = handler.get_realm_index(region.value, region.dynamic_namespace)
        for realm in index['realms']:
            realms.append((region, realm['slug']))

    with app.app_context():
        for region, slug in tqdm(realms):
            db.session.add(WowRealm.create_from_api(handler, region, slug))
        db.session.commit()


def main():
    """Loads static and dynamic data from the WoW Game API in database."""
    args = parser.parse_args()
    if os.path.exists(database_file) and args.recreate_database:
        logging.info('Clearing previous database')
        os.remove(database_file)
    if not os.path.exists(database_file):
        logging.info('Creating database')
        with app.app_context():
            db.create_all()

    preload_realms()


if __name__ == "__main__":
    main()
