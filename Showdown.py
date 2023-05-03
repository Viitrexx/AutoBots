import docker
import re
import time

# Replace these strings
psuser1 = "user1"
psuser2 = "user2"
pspw1 = "pw1"
pspw2 = "pw2"

env1 = ["WEBSOCKET_URI=sim.smogon.com:8000", f"PS_USERNAME={psuser1}", f"PS_PASSWORD={pspw1}", "BOT_MODE=CHALLENGE_USER", f"USER_TO_CHALLENGE={psuser2}", "RUN_COUNT=1", "LOG_LEVEL=DEBUG", "SAVE_REPLAY=True"]
env2 = ["WEBSOCKET_URI=sim.smogon.com:8000", f"PS_USERNAME={psuser2}", f"PS_PASSWORD={pspw2}", "BOT_MODE=ACCEPT_CHALLENGE", "RUN_COUNT=1", "SAVE_REPLAY=True"]

winnerpattern = re.compile("\[DEBUG\]\s*Winner:\s*(?P<name>[A-Za-z0-9]+)")
replaypattern = re.compile("\"battle-(?P<url>[A-Za-z0-9\-]+)\"")

waitforlogin = 10 #seconds

class Player:
    def __init__(self, name, team, mode, bot="safest"):
        self.name = name
        self.team = team
        self.mode = mode
        self.bot = bot
        self.info = f"{team}-{bot}"

def play(player1, player2, **params):
    winner = None
    description = ""
    # docker run --env-file env showdown
    client = docker.from_env()
    client.containers.prune(filters={'label':'autobots'})
    # set TEAM_NAME, POKEMON_MODE, and BATTLE_BOT
    client.containers.run("showdown", name="Player2", environment=env2 + [f"TEAM_NAME={player2.team}", f"POKEMON_MODE={player2.mode}", f"BATTLE_BOT={player2.bot}"], detach=True, labels=['autobots'])
    time.sleep(waitforlogin) # give player 2 some time to log in successfully
    output = client.containers.run("showdown", name="Player1", environment=env1 + [f"TEAM_NAME={player1.team}", f"POKEMON_MODE={player1.mode}", f"BATTLE_BOT={player1.bot}"], labels=['autobots']).decode('utf-8')
    for line in output.split('\n'):
        m = winnerpattern.match(line)
        if m:
            if m['name'] == psuser1:
                winner = True
            elif m['name'] == psuser2:
                winner = False
        n = replaypattern.search(line)
        if n:
            description = f"https://replay.pokemonshowdown.com/{n['url']}"
    score = "1-0" if winner else "0-1"
    return winner, score, description
