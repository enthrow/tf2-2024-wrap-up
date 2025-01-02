"""
***DEPRECIATED***
This was originally a giant helper script that parsed logs and had options to:
- parse nodes and edges with a bunch of filters
- dump nods and edges indifferent formats
- precompute node positions with networkx
- normalize data
etc

It still works but doesn't fit the ecosystem well and is just a bad way of doing it. 
You should probably be generating the db with build_db.py then if you want graph files (csv, json, etc)
or precomputed positions use make_graph.py
"""
import json
import time
import os
import csv
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

def dump_to_json(graph_data: dict, path: str, file_name: str):
    """
    format our data for json use (react-force-graph in mind) then dump it
    """
    
    # output file name stuff
    if not file_name.endswith(".json"):
        file_name += ".json"
    output = path + file_name

    print(f"dumping data to {output}")

    # format nodes
    nodes = []
    for node_id, attributes in graph_data["nodes"].items():
        node_data = {
            "id": node_id,
            "val": attributes["val"]
        }
        if "x" in attributes: 
            node_data["x"] = attributes["x"]
        if "y" in attributes:
            node_data["y"] = attributes["y"]
        if "z" in attributes:
            node_data["z"] = attributes["z"]
        nodes.append(node_data)
    # format edges
    edges = [
        {
            "source": source,
            "target": target,
            "val": attributes["val"],
        }
        for (source, target), attributes in graph_data["edges"].items()
    ]

    #dump it
    with open(output, "w") as file:
        json.dump({"nodes": nodes, "links": edges}, file, indent=4) # rename edges > links so its plug and play with react-force-graph

def dump_to_csvs(graph_data: dict, path: str, file_name: str):
    nodes_file = path + file_name + "_nodes.csv"
    edges_file = path + file_name + "_edges.csv"

    print(f"dumping data to {nodes_file} and {edges_file}")

    with open(nodes_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "label", "x", "y", "z", "games_played"])
        writer.writeheader()
        for node_id, attributes in graph_data["nodes"].items():
            writer.writerow({
                "id": node_id,
                "label": node_id,
                "x": attributes.get("x", ""),  # Default to empty if not present
                "y": attributes.get("y", ""),  # Default to empty if not present
                "z": attributes.get("z", ""),  # Default to empty if not present
                "games_played": attributes["val"]
            })

    # Write edges to CSV
    with open(edges_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["source", "target", "weight"])
        writer.writeheader()
        for (source_id, target_id), attributes in graph_data["edges"].items():
            writer.writerow({
                "source": source_id,
                "target": target_id,
                "weight": attributes["val"]
            })

def precompute_positions(graph_data, dimensions):
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
    for (source, target), val in graph_data["edges"].items():
        G.add_edge(source, target, val=val["val"])

    # compute positions, this takes forever
    print("precomputing positions... this could take a while")
    pos = nx.spring_layout(G, dim=dimensions, k=None, scale=10000)

    # update graph_data
    for node_id, coordinates in pos.items():
        if dimensions == 2:
            graph_data["nodes"][node_id]["x"] = coordinates[0]
            graph_data["nodes"][node_id]["y"] = coordinates[1]
        elif dimensions == 3:
            graph_data["nodes"][node_id]["x"] = coordinates[0]
            graph_data["nodes"][node_id]["y"] = coordinates[1]
            graph_data["nodes"][node_id]["z"] = coordinates[2]
    return graph_data

def normalize_logarithmically(graph_data):
    """
    lets try logarithmic scaling instead! 
    """
    print("normalizing edge weights")
    weights = np.array([d['val'] for d in graph_data["edges"].values()]).reshape(-1, 1)

    log_weights = np.log1p(weights)

    # normalize to the range [0, 1]
    normalized_weights = (log_weights - log_weights.min()) / (log_weights.max() - log_weights.min())

    # put it back in the dict as proper types
    graph_data["edges"] = {
        key: {'val': float(val.item() if hasattr(val, "item") else val)}
        for key, val in zip(graph_data["edges"].keys(), normalized_weights)
    }    
    return graph_data

def cull_data(graph_data, minimum_logs):
    """
    remove any players that don't have enough logs to meet the defined minimum
    that means all their nodes, all associated edges.
    BROKEN RIGHT NOW, causes a keyerror in precomputing step. IDK what I did wrong.
    """
    print(f"culling nodes with less than {minimum_logs} games.")
    # get every node that has value >= of threshold
    filtered_nodes = {
        id: val
        for id, val in graph_data["nodes"].items()
        if val["val"] >= minimum_logs # good god I need to redo some stuff
    }

    # get set of valid node ids to compare against edges
    valid_nodes = set(filtered_nodes.keys())

    # filter edges where either source or target are in the valid nodes
    filtered_edges = {
        (source, target): val
        for (source, target), val in graph_data["edges"].items()
        if source in valid_nodes or target in valid_nodes
    }

    # return culled data
    return {
        "nodes": filtered_nodes,
        "edges": filtered_edges
    }

def parse_data(log_data: dict, graph_data: dict, gamemodes: list) -> dict:
    """
    get the players out of every log in data, populate our existing graph_data and return it.
    """
    for log in log_data["logs"]:
        blue_players = log["blue"]["players"] # no .get, its slower and my dataset always has these keys so not worried about keyerrors
        red_players = log["red"]["players"]
        # Check that its a valid log we care about. At least a player on each team, and one of the defined gamemodes
        if blue_players is not None and red_players is not None and log["format"] in gamemodes: # i should probably sort out some garbage logs as well (by duration, players per gamemode etc)
            players = blue_players + red_players
            # HANDLE NODES
            for player in players:
                graph_data["nodes"][player]["val"] += 1

            # HANDLE KEYS
            for player1, player2 in combinations(players, 2): # get every combination of 2 players
                link_key = tuple(sorted((player1, player2))) # sorted tuple of the keys so we avoid duplicates. i.e (a,b) always, never (b,a)
                graph_data["edges"][link_key]["val"] += 1

    return graph_data
            

def main():
    parser = argparse.ArgumentParser(description='parse log pages from trends.tf into a format we can use')
    parser.add_argument("-i", "--input", type=str, required=True, help='path to directory with json formatted log pages')
    parser.add_argument("-o", "--output", type=str, required= True, help='output directory.')
    parser.add_argument("-g", "--gamemodes", type=str, nargs="+", default=["sixes", "highlander"],  help="gamemodes to consider. trends provides sixes, highlander, ultiduo, fours, prolander, other")
    parser.add_argument("-m", "--minlogs", type=int, default=None,  help="minimum amount of games a player needs to have to be a node")
    parser.add_argument("-n", "--normalize", action="store_true",  help="normalize the data")
    parser.add_argument("-p", "--precompute", type=int, choices=[2,3], help="precompute the data with networkx spring_layout with specified dimensions")
    parser.add_argument("-j", "--json", type=str, help="dump log data to a json file formatted for react-force-graph")
    parser.add_argument("-c", "--csv", type=str, help="dump node and edge files for gephi etc")
    # parser.add_argument("--info", action="store_true", help="run graph_info after completion to get some data") 

    args = parser.parse_args()

    input_path = args.input
    output_directory = args.output
    gamemodes = args.gamemodes
    minimum_logs = args.minlogs
    normalize = args.normalize
    precompute = args.precompute
    json_file = args.json
    csv_file = args.csv
    # get_info = args.info
    
    print(gamemodes)

    # make sure we have somewhere to put our output
    if json_file is None and csv_file is None:
        print("no output format specified. use --json or --csv")
        exit()
    
    start_time = time.time()
    graph_data = {
        "nodes": defaultdict(lambda: {"val": 1}),
        "edges": defaultdict(lambda: {"val": 1}),
    }

    # parse all the logs
    print("parsing logs")
    for filename in os.listdir(input_path):
        file_path = os.path.join(input_path, filename)
        if os.path.isfile(file_path):  
            log_data = get_logs_from_json(file_path)
            graph_data = parse_data(log_data, graph_data, gamemodes)

    if minimum_logs:
        graph_data = cull_data(graph_data, minimum_logs)
    if normalize:
        graph_data = normalize_logarithmically(graph_data)
    if precompute:
        graph_data = precompute_positions(graph_data, precompute)
    
    # dump to json
    if json_file:
        dump_to_json(graph_data, output_directory, json_file)
    # dump to csv
    if csv_file:
        dump_to_csvs(graph_data, output_directory, csv_file)

    end_time = time.time()
    runtime = end_time - start_time
    print(f"generated graph positional data with {len(graph_data["nodes"])} nodes and {len(graph_data["edges"])} edges in {runtime} seconds")
if __name__ == "__main__":
    main()
