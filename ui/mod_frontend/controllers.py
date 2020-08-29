"""Controller utilities for authentication through Discord."""

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

from flask import Blueprint, send_from_directory
from werkzeug.exceptions import NotFound

from config.flask import debug

mod_frontend = Blueprint('frontend', __name__)


# Prevent cached response when running in debug mode, so we can easily
# rebuild on change and see the differences.
if debug:
    @mod_frontend.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


@mod_frontend.route('/<path:path>')
def frontend_proxy(path):
    """Serves the unbound paths from the Angular compiled directory."""
    try:
        return send_from_directory('./web/dist', path)
    except NotFound:
        # Fallback to the index.html. It is fairly possible the requested route
        # is the result of Angular attempting to route to itself.
        return send_from_directory('./web/dist', 'index.html')
