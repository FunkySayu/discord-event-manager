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

from api.base import app, db
from api.mod_auth.controllers import mod_auth
from api.mod_frontend.controllers import mod_frontend
from api.mod_guild.controllers import mod_guild
from api.mod_event.controllers import mod_event
from api.mod_user.controllers import mod_user
from api.mod_wow.controllers import mod_wow

db.init_app(app)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_frontend)
app.register_blueprint(mod_guild)
app.register_blueprint(mod_event)
app.register_blueprint(mod_user)
app.register_blueprint(mod_wow)


@app.route('/')
def root():
    """Serves the root index file."""
    return send_from_directory('../web/dist', 'index.html')


@app.errorhandler(500)
def internal_server_error(e):
    """Friendly wrapper around a 500 error."""
    return render_template('500.html', error=repr(e)), 500
