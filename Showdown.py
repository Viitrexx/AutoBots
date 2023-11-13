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

winnerpattern = re.compile(r"\[DEBUG\]\s*Winner:\s*(?P<name>[A-Za-z0-9 -_!#%€.\\\/]+)")
replaypattern = re.compile(r"battle-(?P<url>[A-Za-z0-9\-]+)\|\/savereplay")

waitforlogin = 10 #seconds

class Player:
    def __init__(self, name, team, mode, bot="safest", avatar="heroine-conquest"):
        self.name = name
        self.team = team
        self.mode = mode
        self.bot = bot
        self.info = f"{team}-{bot}"
        self.avatar = avatar

def play(player1, player2, **params):
    big_description = ""
    p1score = 0
    p2score = 0
    not_done = True
    winner = None
    best_of = 3
    
    while not_done:
        description = ""
        # docker run --env-file env showdown
        client = docker.from_env()
        pruned = client.containers.prune(filters={'label':'autobots'})
        # sometimes Player2 is not pruned
        ok = False
        while not ok:
            try:
                # set TEAM_NAME, POKEMON_MODE, and BATTLE_BOT
                client.containers.run("showdown", name="Player2", environment=env2 + [f"TEAM_NAME={player2.team}", f"POKEMON_MODE={player2.mode}", f"BATTLE_BOT={player2.bot}", f"AVATAR={player2.avatar}"], detach=True, labels=['autobots'])
                ok = True
            except:
                print("Player2 was not pruned.")
                time.sleep(2)
                client.containers.prune(filters={'label':'autobots'})
        time.sleep(waitforlogin) # give player 2 some time to log in successfully
        output = client.containers.run("showdown", name="Player1", environment=env1 + [f"TEAM_NAME={player1.team}", f"POKEMON_MODE={player1.mode}", f"BATTLE_BOT={player1.bot}", f"AVATAR={player1.avatar}"], labels=['autobots']).decode('utf-8')
        for line in output.split('\n'):
            m = winnerpattern.match(line)
            if m:
                if m['name'] == psuser1:
                    #winner = True
                    p1score += 1
                elif m['name'] == psuser2:
                    #winner = False
                    p2score += 1
            n = replaypattern.search(line)
            if n:
                description = f"https://replay.pokemonshowdown.com/{n['url']}"
        big_description += f"{description}, "
        if p1score > best_of/2.0:
            winner = True
            not_done = False
        elif p2score > best_of/2.0:
            winner = False
            not_done = False
    
    big_description = big_description[:len(big_description)-2] # Remove trailing comma and space
    score = f"{p1score}-{p2score}"
    return winner, score, big_description
