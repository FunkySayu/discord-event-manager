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

import asyncio
import argparse
import logging
import os
import threading

from bot.bot import make_bot_instance
from config.discord import bot_token
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


logging.root.setLevel(logging.INFO)


class DiscordBotRuntimeThread(threading.Thread):
    """Creates a thread environment to run the discord bot.

    Creates a wrapper allowing to wait for the bot initialization as well
    as cleanly shut it down.
    """

    def __init__(self, token: str):
        super().__init__()
        self._token = token
        self._ready = threading.Event()
        self._loop = asyncio.new_event_loop()

    def run(self):
        """Runs the thread."""
        asyncio.set_event_loop(self._loop)
        bot = make_bot_instance(loop=self._loop)

        async def runner():
            """Main bot runtime loop."""
            try:
                await bot.start(self._token)
            finally:
                await bot.close()

        async def readiness_notifier():
            """Notifies when the bot is ready the threading.Event."""
            try:
                await bot.wait_until_ready()
            finally:
                self._ready.set()

        self._loop.create_task(runner(),
                               name='Bot runtime')
        self._loop.create_task(readiness_notifier(),
                               name='Readyness notifier')
        self._loop.run_forever()

    def wait_readiness(self):
        """Blocking call waiting for the bot to be fully operational."""
        self._ready.wait()

    def clean_stop(self):
        """Clean stop of the bot, closing all connections."""
        self._loop.stop()
        self.join()


def main():
    """Runs the bot with its frontend server."""
    args = parser.parse_args()
    if not args.no_build:
        logging.info('Building Angular...')
        build_angular(debug)

    if os.path.exists(database_file) and args.recreate_database:
        logging.info('Clearing previous database')
        os.remove(database_file)
    if not os.path.exists(database_file):
        logging.info('Creating database')
        with app.app_context():
            db.create_all()

    # Start the bot
    runner = DiscordBotRuntimeThread(bot_token)
    logging.info('Starting the bot')
    runner.start()
    runner.wait_readiness()
    logging.info('Bot started, starting Flask application')

    host = debug and '127.0.0.1' or '0.0.0.0'
    try:
        app.run(host=host, port=args.port, debug=debug,
                use_reloader=False)
    finally:
        runner.clean_stop()


if __name__ == "__main__":
    main()
