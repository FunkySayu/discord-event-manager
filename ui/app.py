"""Flask web application definition."""

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

from flask import send_from_directory, render_template

from ui.base import app, db
from ui.mod_auth.controllers import mod_auth
from ui.mod_frontend.controllers import mod_frontend
from ui.mod_guild.controllers import mod_guild
from ui.mod_event.controllers import mod_event
from ui.mod_user.controllers import mod_user

db.init_app(app)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_frontend)
app.register_blueprint(mod_guild)
app.register_blueprint(mod_event)
app.register_blueprint(mod_user)


@app.route('/')
def root():
    """Serves the root index file."""
    return send_from_directory('./web/dist', 'index.html')


@app.errorhandler(500)
def internal_server_error(e):
    """Friendly wrapper around a 500 error."""
    return render_template('500.html', error=repr(e)), 500
