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

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def root():
    """Serves the root index file."""
    return render_template('index.html')


@app.errorhandler(500)
def internal_server_error(e):
    """Friendly wrapper around a 500 error."""
    return render_template('500.html', error=repr(e)), 500
