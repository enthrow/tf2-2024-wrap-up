import json

with open('data/test_data/example_page.json', 'r') as file:
    data = json.load(file)


# blue_players = []
# for log in data['logs']: # for every log
#     for player in log['blue']['players']:
#         blue_players.append(player)

# testing stuff
blue_players = [player for log in data['logs'] for player in log['blue']['players']]
red_players = [player for log in data['logs'] for player in log['red']['players']]
total_players = red_players + blue_players
print(len(blue_players))
print(len(red_players))
print(len(total_players))
print(len(set(total_players)))

"""
mock function:
for every log:
    add every player as a node if they aren't already
    if they are a player, increase their games played by 1
    for every combination of players
        if there isn't a link already make one
        if there is, increase weight by 1



    Only then do we figure out how we want to handle extra types of links
    (teammates, gamemodes, etc)

    right now this will just do games played in the same server which is kinda off
"""

graph_data = {
    "nodes": [],
    "links": []
}

for log in data['logs']: # for every log
    for player in log['blue']['players'] + log['red']['players']: # for every player
        if not any(player in d['id'] for d in graph_data['nodes']): # if we don't have a node with this id
            player_node = { # define a player_node dict to add to nodes
                "id":player,
                "games":1
                }
            graph_data['nodes'].append(player_node) # add it

        else: # if we have a node already and just need to update it
            for node in graph_data['nodes']:
                if node['id'] == player:
                    node['games'] += 1
                    break # just the first instance, there better not be multiple nodes I'll jump out a building


# write it baby
with open("test.json", "w") as file:
    json.dump(graph_data, file, indent=4)