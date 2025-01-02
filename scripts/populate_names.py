"""
Another helper script.
Goes through our logs.db and uses RGL and ETF2L APIs (and kinda just checks ozf without an API) to fill in names.
Also spits out name_map.csv for later use.
If --csv is specified it will instead populate the DB from that to avoid all the API calls.
If you are using the existing dataset available in this repo please do that instead of hugging these cool community league APIs.
name_map.csv is available in /data for your mapping pleasure.

This is probably wildly inefficient because we make such frequent commits to the db,
but ratelimits happen and its nice to be able to just pick up where you left off.
"""
import requests
import csv
import time
import re
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Player

def load_map(path) -> dict:
    """
    if we have it, just get the map of id:name from the csv file
    """
    print("getting map from csv")
    id_name_map = {}
    with open(path, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader) # skip header row
        for row in csv_reader:
            id_name_map[row[0]] = row[1]
    return id_name_map

def dump_csv(session, path="data/name_map.csv"):
    """
    dump to a csv for later use
    """
    try:
        # query all players with non-null and non-empty names
        players = session.query(Player).filter(Player.name != None, Player.name != "").all()
        
        # write em
        with open(path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name"])
            for player in players:
                writer.writerow([player.id, player.name])

        print(f"exported {len(players)} players to {path}.")
    except Exception as e:
        print(f"Error exporting players to CSV: {e}")

def check_csv(session, id_name_map):
    """
    try to fill in any missing names in the db from the map from our csv file
    """
    print("populating names from csv")
    try:
        # query players still with missing or empty names
        players_to_update = session.query(Player).filter((Player.name == None) | (Player.name == "")).all()

        for player in players_to_update:
            if str(player.id) in id_name_map:
                player.name = id_name_map[str(player.id)]
                print(f"found name for {player.id}: {player.name}")
                try:
                    session.commit()
                except Exception as commit_error:
                    print(f"failed to commit changes for {player.id}: {commit_error}")
                    session.rollback()

        print("filled in all names from csv")
    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"error updating player name: {e}")


def check_rgl(session):
    """
    try to fill in any missing names in the db from rgl
    """
    print("finding rgl names...")
    chunk_size = 25 # we do 25 at a time for RGL, pretty sure that's the limit
    try:
        # query players with missing or empty names
        players_to_update = session.query(Player).filter((Player.name == None) | (Player.name == "")).all()

        # split players into batches
        ids = [player.id for player in players_to_update]
        for i in range(0, len(ids), chunk_size):
            chunk = ids[i:i + chunk_size]
            updated_chunk = get_name_rgl(chunk)

            # update names in the database
            for player in players_to_update:
                if player.id in updated_chunk:
                    player.name = updated_chunk[player.id]
                    print(f"found rgl name for {player.id}: {player.name}")
            try:
                session.commit()
            except Exception as commit_error:
                print(f"failed to commit batch starting with ID {chunk[0]}: {commit_error}")
                session.rollback()

        print("found all rgl player names")
    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"error updating player names after rgl pass: {e}")

def check_etf2l(session):
    """
    try to fill in any missing names in the db from etf2l
    """
    print("finding etf2l names...")
    try:
        # query players still with missing or empty names
        players_to_update = session.query(Player).filter((Player.name == None) | (Player.name == "")).all()

        for player in players_to_update:
            name = get_name_etf2l(player.id)
            if name is not None and name !=  "":
                player.name = name
                print(f"found etf2l name for {player.id}: {player.name}")
                try:
                    session.commit()
                except Exception as commit_error:
                    print(f"failed to commit changes for {player.id}: {commit_error}")
                    session.rollback()
            time.sleep(1.6) # fuckin rate limits- seem to vary wildly even though it should be 60/min.

        print("found all etf2l names.")
    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"error updating player names after etf2l pass: {e}")

def check_ozf(session):
    """
    try to fill in any missing names in the db from ozf.
    """
    print("finding ozf names...")
    try:
        # query players still with missing or empty names
        players_to_update = session.query(Player).filter((Player.name == None) | (Player.name == "")).all()

        for player in players_to_update:
            name = get_name_ozf(player.id)
            if name is not None and name !=  "":
                player.name = name
                print(f"found ozf name for {player.id}: {player.name}")
                try:
                    session.commit()
                except Exception as commit_error:
                    print(f"failed to commit changes for {player.id}: {commit_error}")
                    session.rollback()
            # time.sleep(1.5) # fuckin rate limits

        print("found all ozf names.")
    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"error updating player names after ozf pass: {e}")

def get_name_rgl(ids: list) -> dict:
    """
    check batch of ids with the rgl api, return a dict of them. batching is so nice here ty 24.
    """
    now = time.time()
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))

    print(f"hitting rlg api {now}")
    updated_chunk = {}
    url = "https://api.rgl.gg/v0/profile/getmany"
    response = requests.post(url, json=list(map(str, ids)))
    if response.status_code == 200:
        return_data = response.json()
        # print(return_data)
        for player_data in return_data:
            updated_chunk[int(player_data["steamId"])] = player_data["name"]
        return updated_chunk
    elif response.status_code == 404: # all players in the chunk weren't RGL isn't that nuts
        return updated_chunk

    else:
        print(f"kill kyle: {response.status_code}") # IM FUCKING RATE LIMITED KYLE
        print(f"was trying to get info on {ids} when something BAD happened.")
        exit() # just so we don't get banned or whatever


def get_name_etf2l(id: int) -> str: 
    """
    hug the free community league's API. get name from id.
    """
    # print(f"checking {id}")
    url = "https://api-v2.etf2l.org/player/" + str(id)
    response = requests.get(url)
    if response.status_code == 200:
        return_data = response.json()
        # print(return_data)
        name = return_data["player"]["name"]
        return name
    
    elif response.status_code == 404: # not an etf2l guy
        return None

    else:
        print(f"error getting etf2l data for {id}: {response.status_code}") # free league got my ass
        exit() # just so we don't get banned or whatever

def get_name_ozf(id: int) -> str: 
    """
    OZF supposedly has an API, but I am too antisocial to join a discord for it.
    I am scraping and not even doing it well. Literally just looking for page title with regex.
    This is lazy and not particularly nice. OZF site maintainer whoever you are, I will send you money for
    these page hits if you wish.
    """
    url = "https://ozfortress.com/users/steam_id/" + str(id)
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content.decode("utf-8") # decode response
        match = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE) # fucking regex for the title of the page.
        if match:
            return match.group(1).strip()
    elif response.status_code == 404: # not an ozf guy
        return None

            
    else:
        print(f"error getting ozf data for {id}: {response.status_code}") # whoops
        exit() # just so we don't get ip banned or whatever

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description='populate names in the database. if more than 1 method is specified, will always try in the order csv > rgl > etf2l > ozf')
    parser.add_argument('--csv', type=str, help='path to existing id:name csv')
    parser.add_argument('--rgl', action="store_true", help='check with rgl api')
    parser.add_argument('--etf2l', action="store_true", help='check with etf2l api')
    parser.add_argument('--ozf', action="store_true", help='check by scraping ozf')

    args = parser.parse_args()

    csv_file = args.csv
    rgl = args.rgl
    etf2l = args.etf2l
    ozf = args.ozf

    # init db stuff
    engine = create_engine('sqlite:///logs.db')
    Session = sessionmaker(bind=engine)
    session = Session()


    if not any(csv_file, rgl, etf2l, ozf):
        print("no method specified, not doing anything. -h for help.")
        exit()
    if not csv_file:
        print("No csv file specified, populating names with specified APIs. This could take a very long time.")
        print("If you have a csv of id:name please consider using that to cut down on runtime.")
    if csv_file:
        id_name_map = load_map(csv_file)
        check_csv(session, id_name_map)
    if rgl: check_rgl(session)
    if etf2l: check_etf2l(session)
    if ozf: check_ozf(session)
    dump_csv(session)
    
    end_time = time.time()
    runtime = end_time - start_time
    print(f"done in {runtime} seconds")

if __name__ == "__main__":
    main()