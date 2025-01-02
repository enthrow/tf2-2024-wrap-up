"""
Build graph files from data in the db.
"""
import time
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Player, Game, PlayerGame

def parse(session) -> dict:
    """
    parse data in the db into a graph dict made up of nodes and edges.
    """
    graph = {
        "nodes": {},
        "edges": {} 
    }

    try:
        # query all players
        players = session.query(Player).all()

        # add nodes
        for player in players:
            total_games = session.query(PlayerGame).filter(PlayerGame.player_id == player.id).count()
            graph["nodes"][player.id] = {
                "name": player.name,
                "games": total_games
            }

        # get edges
        all_games = session.query(Game).all()
        for game in all_games:
            # get all players in the curernt game
            player_ids = [pg.player_id for pg in game.players]

            # make or increment an edge for every player in the game
            for i, player1 in enumerate(player_ids):
                for player2 in player_ids[i + 1:]:
                    edge_key = tuple(sorted((player1, player2)))
                    if edge_key not in graph["edges"]:
                        graph["edges"][edge_key] = 0
                    graph["edges"][edge_key] += 1

        return graph
    except Exception as e:
        print(f"some sort of database error parsing graph: {e}")
        return None

def main():
    start_time = time.time()

    # parse args
    parser = argparse.ArgumentParser(description="build graph data from the db")
    parser.add_argument("-n", "--name", type=str, required=True, help="name for this graph")
    parser.add_argument("-f", "--formats", type=str, nargs="+", default=["sixes", "highlander"], help="formats to consider. [sixes, highlander, ultiduo, fours, prolander, other]")
    parser.add_argument("-min", "--minlogs", type=int, default=None, help="minimum amount of games a player needs to have to be a node")
    parser.add_argument("-m", "--modulatrity", type=int, help="run a Louvain modularity algorithm to identify node communities. Requires a resolution int. <1 smaller communities, >1 larger communities")
    parser.add_argument("-p", "--precompute", type=int, choices=[2,3], help="precompute the data with networkx spring_layout in specified number of dimensions")
    parser.add_argument("-j", "--json", action="store_true", help="dump log data to a json file formatted for react-force-graph")
    parser.add_argument("-c", "--csv", action="store_true", help="dump node and edge csvs for gephi etc")

    args = parser.parse_args()

    name = args.name
    formats = args.formats
    minimum_logs = args.minlogs
    modularity = args.modularity
    precompute = args.precompute
    json_file = args.json
    csv_file = args.csv

    # make sure we have somewhere to put our output
    if not json_file and not csv_file:
        print("no output format specified. use --json or --csv")
        exit()

    # init db stuff
    engine = create_engine('sqlite:///logs.db')
    Session = sessionmaker(bind=engine)
    session = Session()

        
    end_time = time.time()
    runtime = end_time - start_time
    print(f"ran in {runtime} seconds")
if __name__ == "__main__":
    main()
