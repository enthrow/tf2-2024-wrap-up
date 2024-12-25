"""
lil script to get a bunch of info about what we've generated.
assumes a json file formatted for force-graph-3d
just for development, I need lots of data to optimize the output/ 
normalize values. Print some garbage, make some graphs
"""
import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
import statistics


def get_data(path) -> dict: 
    """
    open a json file at a path, return its contents as a dict
    """
    with open(path, "r") as file:
        data = json.load(file)
    return data


def plot(data):
    """
    genuinely example copy pasted garbo, plot some histograms about our data.
    """
    node_values = [node["val"] for node in data["nodes"]]
    edge_values = [link["val"] for link in data["links"]]

    node_bins = np.histogram_bin_edges(node_values, bins='auto')
    edge_bins = np.histogram_bin_edges(edge_values, bins='auto')

    # make fig, subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))  # 1 row, 2 columns

    axes[0].hist(node_values, bins=node_bins, color='blue', edgecolor='black')
    axes[0].set_title('Node Values Histogram')
    axes[0].set_xlabel('Node Values')
    axes[0].set_ylabel('Frequency')

    axes[1].hist(edge_values, bins=edge_bins, color='green', edgecolor='black')
    axes[1].set_title('Edge Values Histogram')
    axes[1].set_xlabel('Edge Values')
    axes[1].set_ylabel('Frequency')

    # show it
    plt.tight_layout()
    plt.show()

def print_stats(data):
    # MOST GAMES
    most_games = max(data["nodes"], key=lambda node: node["val"])
    print(f"most games: id = {most_games['id']}, games = {most_games['val']}")

    # MOST EDGES
    most_edges = max(data["links"], key=lambda link: link["val"])
    print(f"most edges: source = {most_edges['source']}, target = {most_edges['target']}, games = {most_edges['val']}")

    # LEAST GAMES
    least_games = min(data["nodes"], key=lambda node: node["val"])
    print(f"least games: id = {least_games['id']}, games = {least_games['val']}")

    # LEAST EDGES
    least_edges = min(data["links"], key=lambda link: link["val"])
    print(f"least edges: source = {least_edges['source']}, target = {least_edges['target']}, games = {least_edges['val']}")

    # MEDIAN GAMES
    node_values = [node["val"] for node in data["nodes"]]
    median_node_val = statistics.median(node_values)
    print(f"median games: {median_node_val}")

    # MEDIAN EDGES
    link_values = [link["val"] for link in data["links"]]
    median_link_val = statistics.median(link_values)
    print(f"median edges: {median_link_val}")

def main():
    parser = argparse.ArgumentParser(description='get some info about our generated react-force-graph json files')
    parser.add_argument('--input', type=str, help='path to graph data json')
    args = parser.parse_args()

    data = get_data(args.input)
    print_stats(data)
    plot(data)

if __name__ == "__main__":
    main()
