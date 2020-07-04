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

from roster.model import Player, Character, CharacterClass, CharacterRole


class TestPlayer(unittest.TestCase):

    def test_good_discord_handle(self):
        """Ensures we can create a player with a good discord handle."""
        player = Player("Foobar#1234", "12345678")
        self.assertEqual(player.discord_handle, "Foobar#1234")

    def test_bad_discord_handle(self):
        """Ensures a bad discord handle fails with a ValueError."""
        with self.assertRaises(ValueError):
            Player("Upsupswrong", "12345678")

    def test_get_all_roles(self):
        """Ensures we can resolve all the roles a player can play."""
        player = Player("Foobar#1234", "12345678", [
            Character("server", "Alice", CharacterClass.HUNTER),
            Character("server", "Bob", CharacterClass.WARRIOR),
        ])
        self.assertEqual(player.get_playable_roles(),
                         {CharacterRole.DPS, CharacterRole.TANK})


if __name__ == '__main__':
    unittest.main()
