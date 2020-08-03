"""Integration with Google Sheets, storing the events."""

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

import unittest

from event.sheet_integration import column_offset


class EventSpreadsheetTest(unittest.TestCase):
    """Unit tests for the event spreadsheet integration."""

    def test_column_offset(self):
        """Tests Google Sheets' column offsets are well calculated."""
        self.assertEqual(column_offset('A'), 0)
        self.assertEqual(column_offset('D'), 3)
        self.assertEqual(column_offset('AA'), 26)
        self.assertEqual(column_offset('AD'), 29)
        self.assertEqual(column_offset('BA'), 52)
        self.assertEqual(column_offset('BD'), 55)


if __name__ == '__main__':
    unittest.main()
