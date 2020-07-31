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

from ui.app import app
from ui.build import build_angular

parser = argparse.ArgumentParser(
  description='Flask application serving the event manager UI.')
parser.add_argument('-p', '--port', dest='port', type=int,
                    help='an integer for the accumulator')
parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                    help='run the application in debug mode')
parser.add_argument('--no_build', dest='no_build', action='store_true',
                    help='do not build the Angular application')


def main():
    """Builds and runs the UI server."""
    args = parser.parse_args()
    if not args.no_build:
        build_angular(args.debug)
    host = args.debug and '127.0.0.1' or '0.0.0.0'
    app.run(host=host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
