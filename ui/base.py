"""The base definition of the Flask application.

This is a low-dependency definition allowing to have minimal test
setup and reducing the risks of cycle dependency in the application.

Runtime application must import app and db from the app.py file.
"""

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

import wtforms_json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

from config.flask import secret_key, database_uri


class BaseSerializerMixin(SerializerMixin):
    """General mixin to use for model serialization in this application.

    This class defines how some special types can be transformed to a simple
    string representing them.
    """
    serialize_types = (
        # Add types and serialization methods here, such as:
        #     (FieldType, lambda (t: FieldType) -> str: ...)
    )


db = SQLAlchemy()

app = Flask(__name__)
app.secret_key = secret_key

# Modification tracking is deprecated and will be removed later. This
# line disables the library warning at runtime.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

# Allow forms to be parsed from JSON.
wtforms_json.init()
