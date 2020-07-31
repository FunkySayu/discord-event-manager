"""Setup script generating the tokens necessary to reach external APIs."""

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
import sys

from config.google import scopes, save_credentials
from google_auth_oauthlib.flow import InstalledAppFlow


parser = argparse.ArgumentParser(
  description='Generates a new Google token given a credentials file')
parser.add_argument('--google_credentials', type=str, default=None,
                    dest='google_credentials',
                    help='path to the Google credentials.json file')


def main():
    """Generates a token from a credentials file, limited to a set of scopes."""
    args = parser.parse_args()

    # Setup Google OAuth2 process.
    google_credentials_path = args.google_credentials
    if google_credentials_path is None:
        google_credentials_path = input(
            'Provide the path to your Google credentials.json file:')
    flow = InstalledAppFlow.from_client_secrets_file(
        google_credentials_path, scopes)
    google_credentials = flow.run_local_server(port=0)

    if not google_credentials:
        print('Failed to generate a Google token.')
        sys.exit(1)

    print('Successfully generated your Google token!')
    save_credentials(google_credentials)


if __name__ == '__main__':
    main()
