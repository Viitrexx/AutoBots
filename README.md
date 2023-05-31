# AutoBots
Depends on https://github.com/ZEDGR/pychallonge.

Run automated challonge brackets for RPS, PokeBots, or whatever you program yourself.  
This repository was made for the SmashCPU Discord.

## Instructions
* Generate an API key at https://challonge.com/settings/developer and put it in `challonge_credentials.txt` along with your username.
* Write a tournament txt file according to one of the examples.
* Run `AutoBots.py` and direct it to your tournament txt file.

## Showdown
Made for the Docker version of https://github.com/pmariglia/showdown.

Put your Pokémon Showdown account information in `Showdown.py`. This has an extra dependency on `docker` which you can get at https://pypi.org/project/docker/.

#### Avatar support

In order to support avatars from https://play.pokemonshowdown.com/sprites/trainers/ you have to edit `run.py` and `config.py`. 

```
# run.py after login()
await ps_websocket_client.send_message('', ['/avatar ' + ShowdownConfig.avatar])
# config.py around configure()
avatar: str
self.avatar = env("AVATAR")
```