# tf2-2024-wrap-up
Some cool data visualization for competitive tf2 in 2024

### todo/ notes
- what kyle did in 2021, so map by games played together but with:
    - links should be:
        - in the same server
        - on the same team
        - each by gamemode maybe?
    - match type
        - rgl (if rgl team?)
        - tf2center (very easy to tell if its a center by log title)
        - format
- interactive site (react-force-graph over d3?)
    - search for player
    - list first and second order relationships on like, the sidebar or whatever



Some additional thoughts:
- rank "best buds" highest number of games played on same team
- finding alts seems pretty easy too with this actually
    - can look for close nodes that never play at the same time, ever.


vaguely what links will look like:
'''
{
    "nodes": [ 
        { 
          "id": "player1_id",
          "name": "alias",
          "games": 1 
        },
        { 
          "id": "player2_id",
          "name": "alias",
          "val": 10 
        },
        ...
    ],
    "links": [
        {
            "source": "player1_id",
            "target": "player2_id",
            "value": "3"
            "type": "shared_logs"
        },
        ...
    ]
}
'''