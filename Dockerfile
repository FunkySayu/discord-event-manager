# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.8.5-alpine3.11

# Set the default working directory
WORKDIR /discord-event-manager
# Copy requirements.txt for depencency resolution
COPY requirements.txt /discord-event-manager

ENV PYTHONPATH /discord-event-manager

# Installing gcc and headers for pip lib building, then installing requirements, then removing gcc
RUN apk add --no-cache --virtual build-dependencies musl-dev gcc \
    && pip install -r requirements.txt \
    && apk del build-dependencies

# Copy file to working directory
# The reason why this section isn't merged with the requirement copy is
# because if we change something in the files, it'll invalidate all subsequent
# layers. We don't want that when it comes to dependencies download, so we put
# the "copy all files" layer after the dependency one
COPY . /discord-event-manager

# Run the program as main.py
CMD ["python","/discord-event-manager/bin/main.py", "--no_build"]
