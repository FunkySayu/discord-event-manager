# Setup

## Discord affiliation

You need to associate the bot with a valid bot registered in Discord.

 - Navigate to https://discordapp.com/developers/applications/
 - Create or select an application
 - In the settings tab, navigate to the Bot section
 - Copy the token and save it as `token.txt` at the root of this repository.

WARNING: never, ever commit the token.txt file to git or you will expose your
bot private key.

## Python setup

Whenever cloning, pulling or pushing a branch, ensure you are running at the
latest version of the specified requirements. A handy way to do so is to use
[virtualenv][virtualenv].

    # Optional: python3 -m pip install --update virtualenv
    python3 -m virtualenv .env
    source .env/bin/activate
    pip install -r requirements

[virtualenv]: https://virtualenv.pypa.io/en/latest/
