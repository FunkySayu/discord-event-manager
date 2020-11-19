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

import json
import os
import unittest.mock

from api.common.testing import DatabaseTestFixture
from api.mod_guild.guild import Guild
from api.mod_user.user import User, UserInGuild, Permission, UserOwnsCharacters
from api.mod_wow.character import WowCharacter
from api.mod_wow.static import WowFaction


TESTDATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'testdata')


class TestUser(DatabaseTestFixture, unittest.TestCase):
    """Checks creation of a user record in the application."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        with open(os.path.join(TESTDATA_DIR,
                               'discord_users_me.json')) as f:
            cls.USER_SESSION_PROFILE = json.load(f)
        with open(os.path.join(TESTDATA_DIR,
                               'discord_users_guilds.json')) as f:
            cls.USER_SESSION_GUILDS = json.load(f)

    def make_discord_session_mock(self):
        """Returns a simple mock on the user session, serving the loaded data."""
        def side_effect(route):
            mock = unittest.mock.MagicMock()
            if route.endswith('@me/guilds'):
                mock.json.return_value = self.USER_SESSION_GUILDS
            else:
                mock.json.return_value = self.USER_SESSION_PROFILE
            return mock

        mock_session = unittest.mock.MagicMock()
        mock_session.get.side_effect = side_effect
        return mock_session

    def test_can_be_created(self):
        """Tests a User instance can be created by simply providing an id."""
        user = User('1234')

        self.db.session.add(user)
        self.db.session.commit()

        actual = User.query.filter_by(id='1234').first()
        self.assertEqual(actual.id, user.id)
        self.assertEqual(actual.date_created, user.date_created)
        self.assertEqual(actual.date_modified, user.date_modified)

    def test_create_from_oauth_discord(self):
        """Checks if a guild can be created from its Discord definition."""
        session = self.make_discord_session_mock()

        actual = User.from_oauth_discord(session)

        self.assertEqual(actual.id, '1357924680')
        self.assertEqual(actual.username, 'FunkySayu')
        self.assertEqual(actual.discriminator, '1357')

    def test_computes_icon_url(self):
        """Tests the user's icon URL is computed from its ID and avatar ID."""
        user = User('1234')
        user.avatar = '5678'

        self.assertEqual(
            user.icon_url,
            'https://cdn.discordapp.com/avatars/1234/5678.png?size=1024')

    def test_register_owned_guilds(self):
        """Checks the user is recorded as an owner of a guild."""
        session = self.make_discord_session_mock()
        self.db.session.add(Guild('111111111111111111'))

        user = User('1357924680')
        user.resync_guild_relationships(session)

        actual = UserInGuild.query.filter_by(user_id=user.id).all()
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0].permission, Permission.owner)
        self.assertEqual(actual[0].guild.id, '111111111111111111')

    def test_register_visible_guilds(self):
        """Checks the user is recorded as an owner of a guild."""
        session = self.make_discord_session_mock()
        self.db.session.add(Guild('2222222222222222222'))

        user = User('1357924680')
        user.resync_guild_relationships(session)

        actual = UserInGuild.query.filter_by(user_id=user.id).all()
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0].permission, Permission.visible)
        self.assertEqual(actual[0].guild.id, '2222222222222222222')

    def test_does_not_register_when_bot_absent(self):
        """Checks it only registers a guild if the bot is present in it."""
        session = self.make_discord_session_mock()

        user = User('1357924680')
        user.resync_guild_relationships(session)

        actual = UserInGuild.query.filter_by(user_id=user.id).all()
        self.assertEqual(len(actual), 0)

    def test_can_own_one_character(self):
        """Checks if the user can own a single character."""
        self.db.session.add(User('123456789'))
        self.db.session.add(
            WowCharacter('987654321', 'Funkypewpew', 13,
                         WowFaction.alliance, 13, 13, 13, 13))

        relationship = UserOwnsCharacters('123456789', '987654321')
        self.db.session.add(relationship)

        actual = User.query.filter_by(id='123456789').first()
        self.assertEqual(len(actual.characters), 1)
        self.assertEqual(actual.characters[0].character.id, '987654321')
