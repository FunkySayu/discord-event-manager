"""Runs all tests."""

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

import glob
import os
import os.path
import unittest


def main():
    """Runs all tests."""
    suites = []
    for fname in glob.glob('**/**_test.py', recursive=True):
        if fname.startswith('venv'):
            # Ensure we do not match tests within our virtual environment.
            continue
        if fname.startswith(os.path.join('web', 'node_modules')):
            # Some files may match in the node module, and use different
            # requirement as ours. Ensure we do not match them.
            continue
        module = fname[:-3].replace(os.path.sep, '.')
        suites.append(unittest.defaultTestLoader.loadTestsFromName(module))

    test_suite = unittest.TestSuite(suites)
    unittest.TextTestRunner().run(test_suite)


if __name__ == '__main__':
    main()
