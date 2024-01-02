import challonge
import time

# Auxiliary functions
def retry(command):
    while True:
        try:
            v = command()
            return v
        except:
            pass

# Read participants from txt file
print("Name of tournament file.txt")
inputt = input()
f = open(f"{inputt}.txt", "r", encoding="utf-8")
ttype = f.readline()[len("Format: "):].strip()
tname = f.readline()[len("Name: "):].strip()
url = f.readline()[len("URL: "):].strip()
participants = f.read().split("\n")
f.close()

players = []

for p in participants:
    if ttype == "RPS":
        from RPS import *
        name, choice = p.split(",")
        print(f"Create player {name.strip()} as {choice.strip()}")
        players.append(Player(name.strip(), choice.strip()))
    elif ttype == "PokeBots":
        from PokeBots import *
        name, typing = p.split(",")
        print(f"Create player {name.strip()} as {typing.strip()}")
        players.append(Player(name.strip(), typing.strip()))
    elif ttype == "Showdown":
        from Showdown import *
        name, team, mode, bot, avatar = p.split(",")
        print(f"Create player {name.strip()} using {team.strip()}")
        players.append(Player(name.strip(), team.strip(), mode.strip(), bot=bot.strip(), avatar=avatar.strip()))
    else:
        assert(False)
    
# Run challonge tournament
f = open("challonge_credentials.txt", "r")
CHALLONGE_USER, CHALLONGE_KEY = f.read().split()
f.close()
challonge.set_credentials(CHALLONGE_USER, CHALLONGE_KEY)

# Delete old tournament
try:
    old_tournament = challonge.tournaments.show(url)
    challonge.tournaments.destroy(old_tournament["id"])
except:
    pass

# Make new tournament
challonge.tournaments.create(tname, url, "double elimination", description=f"Auto-generated tournament using AutoBots. Ran at Unix time {time.time()}.", accept_attachments=True)
tournament = challonge.tournaments.show(url)
for p in players:
    retry(lambda: challonge.participants.create(tournament["id"], p.name))
challonge.participants.randomize(tournament["id"])
challonge.tournaments.start(tournament["id"])

# Run tournament
matches = challonge.matches.index(tournament["id"])
participants = challonge.participants.index(tournament["id"])

def getPlayerById(idd):
    for p in participants:
        if p["id"] == idd:
            for pp in players:
                if pp.name == p["name"]:
                    return pp
                
player_id_dict = {p["id"]: getPlayerById(p["id"]) for p in participants}

def notDone(matches):
    for m in matches:
        if m["state"] == "open":
            return True
    return False

while(notDone(matches)):
    # Get the next match
    m_id = 0
    for m in matches:
        if m["state"] == "open":
            m_id = m["id"]
            break
    # Play it
    print(f"Playing match {m_id}")
    p1 = player_id_dict[m["player1_id"]]
    p2 = player_id_dict[m["player2_id"]]
    winner, score, description = play(p1, p2, best_of=9)
    winner_id = m["player1_id"] if winner else m["player2_id"]
    retry(lambda: challonge.matches.update(tournament["id"], m_id, scores_csv=score, winner_id=winner_id))
    retry(lambda: challonge.attachments.create(tournament["id"], m_id, description=description))
    # Update match list
    matches = retry(lambda: challonge.matches.index(tournament["id"]))

# Add extra info to participant names
for p in participants:
    new_name = f"{p['name']} ({player_id_dict[p['id']].info})"
    retry(lambda: challonge.participants.update(tournament["id"], p["id"], name=new_name))

challonge.tournaments.finalize(tournament["id"])
