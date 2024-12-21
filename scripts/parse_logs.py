"""
Parse our unreasonably large folder of json files into something react-force-graph can use
"""
import json

def get_logs_from_json(path, file_number: int = None) -> dict: 
    """
    Open a json file at a path, return its contents as a dict
    We assume a bunch of files with a similar naming schemes, so we take a path and number and get the path that way.
    We don't bother if one isn't defined.
    """
    # gross but who cares we run it once
    if file_number is not None:
        split_path = path.split(".")
        path = split_path[0] + str(file_number) + "." + split_path[1]
        print(path)

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
    for log in log_data['logs']: # for every log
        players = log['blue']['players'] + log['red']['players']
        seen_players = []
        for player in players: # for every player
            # SOURCES STUFF
            if not any(player in d['id'] for d in graph_data['nodes']): # if we don't have a node with this id
                player_node = { # define a player_node dict to add to nodes
                    "id":player,
                    "games":1
                    }
                graph_data['nodes'].append(player_node) # populate it

            # if we have a node already and just need to update it
            else:
                for node in graph_data['nodes']: # fuck dictionaries
                    if node['id'] == player:
                        node['games'] += 1
                        break # just the first instance, there better not be multiple nodes I'll jump out a building
        
            # LINKS STUFF
            for other_player in players:
                if other_player is not player and other_player not in seen_players:
                    # check for a link
                    existing_link = None
                    for link in graph_data['links']:
                        if (link['source'] == player and link['target'] == other_player) or \
                        (link['source'] == other_player and link['target'] == player):
                            existing_link = link
                            break  # stop searching once the link is found

                    if existing_link: # add a link if 
                        existing_link['value'] += 1
                    else:
                        # If no link exists, create a new one
                        new_link = {
                            "source": player,
                            "target": other_player,
                            "value": 1,
                            "type": "default"  # don't know what to call this in the default case
                        }
                        graph_data['links'].append(new_link)
            
            seen_players.append(player)
                        

    return graph_data

def main():
    graph_data = {
    "nodes": [],
    "links": []
    }

    log_data = get_logs_from_json("data/test_data/example_page.json")
    graph_data = parse_data(log_data, graph_data)
    dump_graph_data(graph_data, "test_output.json")


if __name__ == "__main__":
    main()