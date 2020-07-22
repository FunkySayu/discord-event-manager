#!/usr/bin/env python3

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

import asyncio
import logging

from tabulate import tabulate

from event.sheet_integration import get_default_sheet_handler


async def main():
    """Pulls the list of players present in the spreadsheet.

    Fairly simple script retrieving all the players from the configured
    spreadsheet and displaying them in a table. Useful to manually test
    integration with the spreadsheet.
    """
    logging.getLogger().setLevel(logging.DEBUG)

    handler = get_default_sheet_handler()
    events = await handler.get_events()
    data = []
    for event in events:
        data.append([event.date.isoformat(), event.title, event.description])

    print(tabulate(data, headers=["Date", "Title", "Description"]))


if __name__ == "__main__":
    asyncio.run(main())
