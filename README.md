# Discord bot for event management

This repository provides a [Discord][discord] bot allowing to manage events
directly in [Discord][discord]. The primary use case will be focused around
World of Warcraft raid management, allowing raid leaders / guild masters to
better handle sign up, benching and reminders.

## How does it work?

TODO: add a doc to explain how to setup the bot once... well once we have a bot.

### Administration

Members of a group designated by the Discord server's owner may administrate and
manage the events created by the bot. Management of an event involves:

- creating, editing or removing events
- broadcast a reminder to people who didn't sign up (and be very annoying, to
ensure they'll subscribe)
- decide who will NOT participate to the event in case too many people signed up
(aka "benching")

### Participation

This bot will watch for discord users within a group designated by the Discord
server's owner. People of this group will be able to sign up or mark themselves
as unavailable. If they didn't and the admins are unhappy about that, they'll
receive a reeeeeally friendly message <3

## Source Code Headers

Every file containing source code must include copyright and license
information. This includes any JS/CSS files that you might be serving out to
browsers. (This is to help well-intentioned people avoid accidental copying that
doesn't comply with the license.)

Apache header:

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

# Acknowledgement

This leverages and uses the [Discord.py API][discordpy] under MIT License.

[discord]: http://discordapp.com/
[discordpy]: https://github.com/Rapptz/discord.py
