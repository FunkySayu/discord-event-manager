"""Provides direct/indirect interactions endpoints with the Blizzard API"""

from __future__ import annotations

__LICENSE__ = """
Copyright 2021 Google LLC
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

from flask import Blueprint, jsonify, request
from typing import Optional

from config.blizzard import get_wow_handler
from api.base import db

mod_wow = Blueprint('wow', __name__, url_prefix='/api/wow')


@mod_wow.route('/me/characters')
def get_all_characters():
    """Returns all characters owned by the user, using Blizzard's API. """
    return jsonify(error="not implemented")

