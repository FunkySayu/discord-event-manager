#!/usr/env/python3.7

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


import discord

from handlers.registry import DEFAULT_REGISTRY

TOKEN = '!'

client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if not message.content.startswith('!'):
        return

    command_name = message.content.partition(' ')[0][1:]
    if command_name in DEFAULT_REGISTRY.commands:
        await DEFAULT_REGISTRY.commands[command_name](message)
    else:
        await message.channel.send('Unknown command.')


if __name__ == '__main__':
    try:
        with open('token.txt') as f:
            client.run(f.read().strip())
    except FileNotFoundError:
        print('guess you forgot to create token.txt')
