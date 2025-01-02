"""
parse logs from the json files and throw them all in a database
"""
import time
import argparse
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Player, Game, PlayerGame
    
def initialize_database():
    """
    set up the database and return a session 
    """
    print("initializing db")
    engine = create_engine('sqlite:///logs.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def get_logs_from_json(path) -> dict: 
    """
    open a json file at a path, return its contents as a dict
    """
    with open(path, "r") as file:
        data = json.load(file)
    return data

def parse_data(session, log_data):
    """
    For every game in a log page, throw all relevant data in a database.
    """
    for log in log_data["logs"]:
        blue_players = log["blue"]["players"]
        red_players = log["red"]["players"]
        player_games = []
        # only process games with at least 1 player on each team and a valid map.
        # there were only ~170 logs with no map and after a quick look they all look kinda wonky. manual re-uploads, 3 players, etc.
        if blue_players and red_players and log["map"] != "":
            # populate Games table
            game = Game(
                logstf_id=log["logid"],
                map=log["map"], 
                format=log["format"], 
                duration=log["duration"], 
                red_score=log["red"]["score"], 
                blue_score=log["blue"]["score"],
            )
            session.add(game)

            # process red team players
            for steam_id in red_players:
                # get or create Player object
                player = session.query(Player).filter_by(id=steam_id).first()
                if not player:
                    player = Player(id=steam_id)
                    session.add(player)

                # create PlayerGame and add to session
                player_game = PlayerGame(player=player, game=game, team="red")
                session.add(player_game)
                player_games.append(player_game)

            for steam_id in blue_players:
                # get or create the Player object
                player = session.query(Player).filter_by(id=steam_id).first()
                if not player:
                    player = Player(id=steam_id)
                    session.add(player)

                # create PlayerGame and add to session
                player_game = PlayerGame(player=player, game=game, team="blue")
                session.add(player_game)
                player_games.append(player_game)

        session.commit()

def main():
    parser = argparse.ArgumentParser(description='parse log pages from trends.tf and throw them in a sqlite database')
    parser.add_argument("-i", "--input", type=str, required=True, help='path to directory with json formatted log pages')
    args = parser.parse_args()
    input_path = args.input

    session = initialize_database()

    start_time = time.time()
    print("parsing logs")
    for filename in os.listdir(input_path):
        file_path = os.path.join(input_path, filename)
        if os.path.isfile(file_path):  
            log_data = get_logs_from_json(file_path)
            parse_data(session, log_data)

    end_time = time.time()
    runtime = end_time - start_time
    print(f"parsed logs and built db in {runtime} seconds")
if __name__ == "__main__":
    main()