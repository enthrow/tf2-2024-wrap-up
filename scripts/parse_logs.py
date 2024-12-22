"""
Parse our unreasonably large folder of json files into something react-force-graph can use
"""
import json
import time
import os
from collections import defaultdict
from itertools import combinations

def get_logs_from_json(path) -> dict: 
    """
    Open a json file at a path, return its contents as a dict
    """
    with open(path, "r") as file:
        data = json.load(file)
    return data

def dump_graph_data(graph_data: dict, path):
    """
    dump all the graph_data to a json file for use in react-force-graph.
    to do this, we need to make nodes and links dictionaries of lists instead of dictionaries of dictionaries.
    We do dictionaries because there are literally millions of 
    """
    # convert
    graph_data = {
        "nodes": [
            {"id": node_id, "val": data["val"]}
            for node_id, data in graph_data["nodes"].items()
        ],
        "links": [
            {"source": source, "target": target, "val": data["val"]}
            for (source, target), data in graph_data["links"].items()
        ],
    }

    # dump
    with open(path, "w") as file:
        json.dump(graph_data, file, indent=4)


def parse_data(log_data: dict, graph_data: dict) -> dict:
    """
    get the players out of every log in data, populate our existing graph_data and return it.
    aka dictionary hell. there are so many loops here doing dictionary shit and none of it is pretty.

    right now this will just do games played in the same server. Long term we want additional links for:
    - friendly team
    - enemy team
    - formats
        - 6s, hl
    - maybe something sneaky to see alts we shall see its not really in the spirit of the project

    mock:
    iterate through a log once and every time we do that:
        make a node with defaultdict if there isn"t one
        if there is one, incriment the val key by 1

        then for keys:
        for every other player in the log:
            if there isn"t a link already
                make a new link between our player and the other with val 1
            if there is one, incriment the val key by 1
    """
    for log in log_data["logs"]:
        print(f"parsing log data for {log["logid"]}")
        blue_players = log["blue"]["players"] # no .get, its slower and my dataset always has these keys so not worried about keyerrors
        red_players = log["red"]["players"]
        # we check that these aren"t none before trying to add them. we don"t want logs without at least 1 player on each team anyways
        if blue_players is not None and red_players is not None:
            players = blue_players + red_players
            # HANDLE NODES
            for player in players:
                graph_data["nodes"][player]["val"] += 1

            # HANDLE KEYS
            for player1, player2 in combinations(players, 2): # get every combination of 2 players
                link_key = tuple(sorted((player1, player2))) # sorted tuple of the keys so we avoid duplicates. i.e (a,b) always, never (b,a)
                graph_data["links"][link_key]["val"] += 1

    return graph_data
            


def main():
    directory = "data/log_dumps"
    start_time = time.time()
    graph_data = {
        "nodes": defaultdict(lambda: {"val": 1}),
        "links": defaultdict(lambda: {"val": 1}),
    }

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):  
            log_data = get_logs_from_json(file_path)
            graph_data = parse_data(log_data, graph_data)

    dump_graph_data(graph_data, "data/test_data/rewrite.json")

    end_time = time.time()
    runtime = end_time - start_time
    print(f"generated graph data with {len(graph_data["nodes"])} nodes and {len(graph_data["links"])} links in {runtime} seconds")

if __name__ == "__main__":
    main()
