"""Testing utilities for the app."""

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

import os
import tempfile

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from ui.base import db


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
