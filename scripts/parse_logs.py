"""
Parse our unreasonably large folder of json files into something react-force-graph can use
"""
import json
import time
import os
from collections import defaultdict

def get_logs_from_json(path) -> dict: 
    """
    Open a json file at a path, return its contents as a dict
    """
    with open(path, 'r') as file:
        data = json.load(file)
    return data

def dump_graph_data(graph_data: dict, path):
    """
    dump all the graph_data to a json file for use in react-force-graph
    """
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
    """
    nodes = graph_data["nodes"]
    links = graph_data["links"]

    # defaultdict makes my life easier
    node_index = {node["id"]: node for node in nodes}
    link_index = defaultdict(int)  # Track link counts using a defaultdict

    for log in log_data["logs"]:
        print(f"Parsing log {log['logid']}")
        blue_players = log.get("blue", {}).get("players", [])
        red_players = log.get("red", {}).get("players", [])

        if blue_players is not None and red_players is not None:
            players = blue_players + red_players

            for player in players:
                if player not in node_index:
                    node_index[player] = {"id": player, "games": 1}
                else:
                    node_index[player]["games"] += 1

            for i, player in enumerate(players):
                for j in range(i + 1, len(players)):  # only consider pairs once
                    other_player = players[j]
                    link_key = tuple(sorted([player, other_player]))
                    link_index[link_key] += 1

    # Convert node_index and link_index back to list format
    graph_data["nodes"] = list(node_index.values())
    graph_data["links"] = [
        {"source": source, "target": target, "value": value}
        for (source, target), value in link_index.items()
    ]

    return graph_data

def main():
    directory = "data/log_dumps"
    start_time = time.time()
    graph_data = {
    "nodes": [],
    "links": []
    }

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):  
            log_data = get_logs_from_json(file_path)
            graph_data = parse_data(log_data, graph_data)

    dump_graph_data(graph_data, "data/test_data/maybe.json")

    end_time = time.time()
    runtime = end_time - start_time
    print(f"generated graph data with {len(graph_data['nodes'])} nodes and {len(graph_data['links'])} links in {runtime} seconds")

if __name__ == "__main__":
    main()