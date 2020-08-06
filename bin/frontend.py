"""Flask web runtime script."""

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
import os

from config.flask import port, debug, database_file
from ui.app import app, db
from ui.build import build_angular

parser = argparse.ArgumentParser(
  description='Flask application serving the event manager UI.')
parser.add_argument(
    '-p', '--port', dest='port', type=int, default=port,
    help='web application serving port')
parser.add_argument(
    '--no_build', dest='no_build', action='store_true',
    help='do not build the Angular application')
parser.add_argument(
    '--recreate_database', dest='recreate_database', action='store_true',
    help='if present, removes the previous database file')


def main():
    """Builds and runs the UI server."""
    args = parser.parse_args()
    if not args.no_build:
        print('Building Angular...')
        build_angular(debug)

    if os.path.exists(database_file) and args.recreate_database:
        print('Clearing previous database')
        os.remove(database_file)
    if not os.path.exists(database_file):
        print('Creating database')
        with app.app_context():
            db.create_all()

    host = debug and '127.0.0.1' or '0.0.0.0'
    app.run(host=host, port=args.port, debug=debug)


if __name__ == '__main__':
    main()
