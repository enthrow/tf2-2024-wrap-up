"""
Parse our unreasonably large folder of json files into something react-force-graph can use
"""
import json
import time
import os
import argparse
from collections import defaultdict
from itertools import combinations
import networkx as nx
import numpy as np

def get_logs_from_json(path) -> dict: 
    """
    open a json file at a path, return its contents as a dict
    """
    with open(path, "r") as file:
        data = json.load(file)
    return data

def precompute_positions(graph_data):
    """
    our dataset is likely to be much too big to be rendered at runtime with react-force-graph (ask me how i know)
    for this reason we precompute coordinate data with networkx and pass that to the frontend later.
    uses networkx's spring_layout algo. Still needs some decent tweaking. 
    """
    G = nx.Graph()

    # add nodes
    for node_id, val in graph_data["nodes"].items():
        G.add_node(node_id, val=val["val"]) 

    # add edges
    for (source, target), val in graph_data["links"].items():
        G.add_edge(source, target, val=val["val"])

    # compute positions, this takes forever
    print("precomputing positions... this could take a while")
    pos = nx.spring_layout(G, dim=3, k=None, scale=10000)

    # add positions
    for node_id, coordinates in pos.items():
        G.nodes[node_id]["position"] = {"x": coordinates[0], "y": coordinates[1], "z": coordinates[2]}

    # convert for use in react-force-graph-3d
    output_data = {
        "nodes": [
            {
                "id": node,
                "val": G.nodes[node]["val"],
                "x": G.nodes[node]["position"]["x"],
                "y": G.nodes[node]["position"]["y"],
                "z": G.nodes[node]["position"]["z"]
            }
            for node in G.nodes
        ],
        "links": [
            {
                "source": source,
                "target": target,
                "val": G.edges[source, target]["val"]
            }
            for source, target in G.edges
        ]
    }
    # return properly formatted positional data
    return output_data

def normalize_edge_weights(graph_data):
    """
    lets try logarithmic scaling instead! 
    """
    print("normalizing edge weights")
    weights = np.array([d['val'] for d in graph_data["links"].values()]).reshape(-1, 1)

    log_weights = np.log1p(weights)

    # normalize to the range [0, 1]
    normalized_weights = (log_weights - log_weights.min()) / (log_weights.max() - log_weights.min())

    # put it back in the dict as proper types
    graph_data["links"] = {
        key: {'val': float(val.item() if hasattr(val, "item") else val)}
        for key, val in zip(graph_data["links"].keys(), normalized_weights)
    }    
    return graph_data


def dump_graph_data(graph_data: dict, path):
    """
    dump all the graph_data to a json file for use in react-force-graph.
    to do this, we need to make nodes and links dictionaries of lists instead of dictionaries of dictionaries.
    We do dictionaries because there are literally millions of 
    """
    with open(path, "w") as file:
        json.dump(graph_data, file, indent=4)


def parse_data(log_data: dict, graph_data: dict, gamemodes: list) -> dict:
    """
    get the players out of every log in data, populate our existing graph_data and return it.
    """
    for log in log_data["logs"]:
        # print(f"parsing log data for {log["logid"]}")
        blue_players = log["blue"]["players"] # no .get, its slower and my dataset always has these keys so not worried about keyerrors
        red_players = log["red"]["players"]
        # Check that its a valid log we care about. At least a player on each team, and one of the defined gamemodes
        if blue_players is not None and red_players is not None and log["format"] in gamemodes:
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
    parser = argparse.ArgumentParser(description='parse log pages from trends.tf for use in react-force-graph')
    parser.add_argument("--input", type=str, help='path to directory with json formatted log pages')
    parser.add_argument("--output", type=str, help='file path to put output json')
    parser.add_argument("--gamemodes", type=list, default=["sixes", "highlander"],  help="gamemodes to consider")
    parser.add_argument("-n", "--normalize", action="store_true",  help="normalize the data")


    args = parser.parse_args()

    input = args.input
    output = args.output
    gamemodes = args.gamemodes
    normalize = args.normalize

    start_time = time.time()
    graph_data = {
        "nodes": defaultdict(lambda: {"val": 1}),
        "links": defaultdict(lambda: {"val": 1}),
    }
    print("parsing logs")
    for filename in os.listdir(input):
        file_path = os.path.join(input, filename)
        if os.path.isfile(file_path):  
            log_data = get_logs_from_json(file_path)
            graph_data = parse_data(log_data, graph_data, gamemodes)

    if normalize:
        graph_data = normalize_edge_weights(graph_data)
    output_data = precompute_positions(graph_data)
    dump_graph_data(output_data, output)


    end_time = time.time()
    runtime = end_time - start_time

    print(f"generated graph positional data with {len(graph_data["nodes"])} nodes and {len(graph_data["links"])} links in {runtime} seconds")

if __name__ == "__main__":
    main()
