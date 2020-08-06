import unittest

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

import tempfile
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from ui.base import db
from ui.mod_wow.guild import Guild, WowGuild, Region, Faction


class DatabaseTestFixture:
    """Fixture setting up a clean database for each test."""

    db: SQLAlchemy
    app: Flask
    _testdb_handle: int
    _testdb_path: str
    _testdb_uri: str

    def setUp(self):
        """Sets up a clean database to perform queries on."""
        self._testdb_handle, self._testdb_path = tempfile.mkstemp()
        self._testdb_uri = f'sqlite:///{self._testdb_path}'
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = self._testdb_uri
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = db
        self.db.init_app(self.app)

        # Create a fake app context, as if we were in a request.
        self.app.app_context().push()
        self.db.create_all()
        os.close(self._testdb_handle)

    def tearDown(self):
        """Cleans the database for the next test."""
        self.db.session.remove()
        self.db.drop_all()


class TestGuildModel(DatabaseTestFixture, unittest.TestCase):
    """Ensure consistency of the model."""

    def test_create_guild(self):
        """Creates and registers a guild in a database."""
        guild = Guild(123456789)
        guild.discord_name = 'test me'
        self.db.session.add(guild)
        self.db.session.commit()

        queried = Guild.query.filter_by(id=123456789).all()
        self.assertEqual(len(queried), 1)
        self.assertEqual(queried[0].discord_name, 'test me')

    def test_create_wow_guild(self):
        """Creates and register a wow guild in a database."""
        wow_guild = WowGuild(123, Region.eu, 'argent-dawn', 'some-guild')
        wow_guild.faction = Faction.horde
        wow_guild.realm_name = 'Argent Dawn'
        wow_guild.name = 'Some Guild'
        self.db.session.add(wow_guild)
        self.db.session.commit()

        queried = WowGuild.query.filter_by(id=123).all()
        self.assertEqual(len(queried), 1)
        self.assertEqual(queried[0].faction, Faction.horde)
        self.assertEqual(queried[0].region, Region.eu)
        self.assertEqual(queried[0].realm_name, 'Argent Dawn')
        self.assertEqual(queried[0].name, 'Some Guild')

    def test_associate_guilds(self):
        """Verify wow guild and guild assocation work."""
        wow_guild = WowGuild(321, Region.na, 'argent-dawn', 'some-guild')
        wow_guild.faction = Faction.alliance
        self.db.session.add(wow_guild)
        guild = Guild(123)
        guild.wow_guild = wow_guild
        self.db.session.add(guild)
        self.db.session.commit()

        wow_queried: WowGuild = WowGuild.query.filter_by(id=321).first()
        self.assertEqual(wow_queried.guild, guild)

        queried: Guild = Guild.query.filter_by(id=123).first()
        self.assertEqual(queried.wow_guild, wow_guild)
