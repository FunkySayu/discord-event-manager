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

import discord
import json
import os
import unittest.mock

from ui.common.testing import DatabaseTestFixture
from ui.mod_guild.guild import Guild, WowGuild, Region, Faction


TESTDATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'testdata')


class TestGuildModel(DatabaseTestFixture, unittest.TestCase):
    """Ensure consistency of the model."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        with open(os.path.join(TESTDATA_DIR,
                               'get_guild.json')) as f:
            cls.GET_GUILD_DATA = json.load(f)
        with open(os.path.join(TESTDATA_DIR,
                               'get_guild_crest_emblem_media.json')) as f:
            cls.GET_GUILD_CREST_EMBLEM_MEDIA = json.load(f)

    def test_create_guild(self):
        """Creates and registers a guild in a database."""
        guild = Guild(123456789)
        guild.discord_name = 'test me'
        self.db.session.add(guild)
        self.db.session.commit()

        queried = Guild.query.filter_by(id=123456789).all()
        self.assertEqual(len(queried), 1)
        self.assertEqual(queried[0].discord_name, 'test me')

    def test_guild_synchronization_from_discord(self):
        """Creates a guild and synchronize its field from a Discord one."""
        guild = Guild(123456789)
        discord_guild = discord.Guild(state=None, data={
            'name': 'Beep Beep I am a Sheep',
            'id': 123456789,
            'icon': '987654321',
        })

        guild.resync_from_discord_guild(discord_guild)

        self.assertEqual(guild.discord_name, 'Beep Beep I am a Sheep')
        self.assertEqual(guild.id, 123456789)
        self.assertEqual(
            guild.icon_href,
            'https://cdn.discordapp.com/icons/123456789/987654321.webp'
            '?size=1024')
        self.assertEqual(guild.bot_present, True)

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

    def test_create_wow_guild_from_api(self):
        """Test creation from the WoW API results."""
        mock = unittest.mock.MagicMock()
        mock.get_guild.return_value = self.GET_GUILD_DATA
        mock.get_guild_crest_emblem_media.return_value = \
            self.GET_GUILD_CREST_EMBLEM_MEDIA

        guild = WowGuild.create_from_api(mock, Region.eu,
                                         'argent-dawn', 'negative-waves')

        mock.get_guild.assert_called_with(
            'eu', 'profile-eu', 'argent-dawn', 'negative-waves', locale='en_US')
        mock.get_guild_crest_emblem_media.assert_called_with(
            'eu', 'static-eu', 114)
        self.assertEqual(guild.id, 49392850)
        self.assertEqual(guild.region, Region.eu)
        self.assertEqual(guild.name, 'Negative Waves')
        self.assertEqual(guild.name_slug, 'negative-waves')
        self.assertEqual(guild.realm_name, 'Argent Dawn')
        self.assertEqual(guild.realm_slug, 'argent-dawn')
        self.assertEqual(guild.faction, Faction.alliance)
        self.assertEqual(guild.icon_url,
                         'https://render-eu.worldofwarcraft.com/'
                         'guild/tabards/emblem_114.png')
