"""
API to serve player summaries and other neat stuff from the db. 
"""
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine, func, select, and_, or_
from sqlalchemy.orm import sessionmaker, aliased
from models import Player, Game, PlayerGame
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app) # CORS mostly for dev. this probably shouldn't live in prod until I have api like, good.

engine = create_engine('sqlite:///logs.db')
Session = sessionmaker(bind=engine)
session = Session()

def get_playedwith(session, player_id, same_team=True):
    """
    get all players that a specific player has played with,
    filtered by team relationship and sorted by games played together.
    """
    try:
        # determine filter condition for team relationship
        team_condition = (
            PlayerGame.team == session.query(PlayerGame.team)
            .filter(PlayerGame.player_id == player_id)
            .limit(1).scalar_subquery()
        ) if same_team else (
            PlayerGame.team != session.query(PlayerGame.team)
            .filter(PlayerGame.player_id == player_id)
            .limit(1).scalar_subquery()
        )

        game_ids_subquery = select(PlayerGame.game_id).where(PlayerGame.player_id == player_id)

        # query for players played with and number of games played together
        players = (
            session.query(
                Player.id,
                Player.name,
                func.count(PlayerGame.game_id).label("games_played_together")
            )
            .join(PlayerGame, Player.id == PlayerGame.player_id)
            .filter(PlayerGame.game_id.in_(game_ids_subquery))
            .filter(PlayerGame.player_id != player_id)  # exclude original player
            .filter(team_condition)
            .group_by(Player.id, Player.name)
            .order_by(func.count(PlayerGame.game_id).desc())  # sort by games played together descending
            .all()
        )

        # format response
        response = {
            str(player.id): {"name": player.name, "games_played_together": player.games_played_together}
            for player in players
        }
        return response
    except Exception as e:
        print(f"Error retrieving players played with: {e}")
        return []

def get_shared_game_stats(player1_id, player2_id, same_team=None):
    """
    retrieve shared game stats between two players and filter by team if needed.
    """
    try:
        pg1 = aliased(PlayerGame)
        pg2 = aliased(PlayerGame)

        # query shared games
        shared_games_query = (
            session.query(Game, pg1, pg2)
            .join(pg1, Game.id == pg1.game_id)
            .join(pg2, pg1.game_id == pg2.game_id)
            .filter(pg1.player_id == player1_id)
            .filter(pg2.player_id == player2_id)
        )

        # apply a team filter if it is specified
        if same_team is not None:
            if same_team:
                shared_games_query = shared_games_query.filter(pg1.team == pg2.team)
            else:
                shared_games_query = shared_games_query.filter(pg1.team != pg2.team)

        shared_games = shared_games_query.all()
        total_shared_games = len(shared_games)

        map_stats = {}
        format_stats = {}

        # get the stats for shared games
        for game, _, _ in shared_games:
            # count games per map
            if game.map not in map_stats:
                map_stats[game.map] = 0
            map_stats[game.map] += 1

            # coung games per format
            if game.format not in format_stats:
                format_stats[game.format] = 0
            format_stats[game.format] += 1

        # return all our stats
        return {
            "games": shared_games,
            "total_games": total_shared_games,
            "maps": map_stats,
            "formats": format_stats,
        }

    except Exception as e:
        return {"error": str(e)}, 500

class Allies(Resource):
    def get(self):
        """
        handle GET requests to retrieve stats for games where two players were on the same team.
        example: /allies?id1=76561198053796020&id2=76561198205888020
        """
        player1_id = request.args.get("id1", type=int)
        player2_id = request.args.get("id2", type=int)

        if not player1_id or not player2_id:
            return {"error": "Both id1 and id2 must be provided."}, 400

        try:
            player1 = session.query(Player).filter_by(id=player1_id).first()
            player2 = session.query(Player).filter_by(id=player2_id).first()

            if not player1 or not player2:
                return {"error": "One or both players not found."}, 404

            stats = get_shared_game_stats(player1_id, player2_id, same_team=True)
            games = stats["games"]

            # Calculate won/lost/tied
            won = lost = tied = 0
            for game, pg1, _ in games:
                if game.red_score == game.blue_score:
                    tied += 1
                elif pg1.team == "red" and game.red_score > game.blue_score:
                    won += 1
                elif pg1.team == "blue" and game.blue_score > game.red_score:
                    won += 1
                else:
                    lost += 1

            stats = {
                "total_games": stats["total_games"],
                "won": won,
                "lost": lost,
                "ties": tied,
                "maps": stats["maps"],
                "formats": stats["formats"],
            }

            return {
                "player1": {"id": str(player1.id), "name": player1.name},
                "player2": {"id": str(player2.id), "name": player2.name},
                "games": stats,
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500
        
class Enemies(Resource):
    def get(self):
        """
        handle GET requests to retrieve stats for games where two players were on opposite teams.
        example: /enemies?id1=76561198053796020&id2=76561198205888020
        """
        player1_id = request.args.get("id1", type=int)
        player2_id = request.args.get("id2", type=int)

        if not player1_id or not player2_id:
            return {"error": "Both id1 and id2 must be provided."}, 400

        try:
            player1 = session.query(Player).filter_by(id=player1_id).first()
            player2 = session.query(Player).filter_by(id=player2_id).first()

            if not player1 or not player2:
                return {"error": "One or both players not found."}, 404

            stats = get_shared_game_stats(player1_id, player2_id, same_team=False)
            games = stats["games"]

            # Calculate player1_wins/player2_wins/ties
            player1_wins = player2_wins = tied = 0
            for game, pg1, pg2 in games:
                if game.red_score == game.blue_score:
                    tied += 1
                elif pg1.team == "red" and game.red_score > game.blue_score:
                    player1_wins += 1
                elif pg1.team == "blue" and game.blue_score > game.red_score:
                    player1_wins += 1
                elif pg2.team == "red" and game.red_score > game.blue_score:
                    player2_wins += 1
                elif pg2.team == "blue" and game.blue_score > game.red_score:
                    player2_wins += 1

            stats = {
                "total_games": stats["total_games"],
                "player1_wins": player1_wins,
                "player2_wins": player2_wins,
                "ties": tied,
                "maps": stats["maps"],
                "formats": stats["formats"],
            }

            return {
                "player1": {"id": str(player1.id), "name": player1.name},
                "player2": {"id": str(player2.id), "name": player2.name},
                "games": stats,
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500
        
class SharedGames(Resource):
    def get(self):
        """
        handle GET requests to retrieve stats for ALL shared games between two players.
        example: /shared?id1=76561198053796020&id2=76561198205888020
        """
        player1_id = request.args.get("id1", type=int)
        player2_id = request.args.get("id2", type=int)

        if not player1_id or not player2_id:
            return {"error": "Both id1 and id2 must be provided."}, 400

        try:
            player1 = session.query(Player).filter_by(id=player1_id).first()
            player2 = session.query(Player).filter_by(id=player2_id).first()

            if not player1 or not player2:
                return {"error": "One or both players not found."}, 404

            stats = get_shared_game_stats(player1_id, player2_id, same_team=None)
            del stats["games"]  # Remove raw games data from the response

            return {
                "player1": {"id": str(player1.id), "name": player1.name},
                "player2": {"id": str(player2.id), "name": player2.name},
                "games": stats,
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500


class PlayerInfo(Resource):
    def get(self, player_id):
        """
        handle GET for detailed player data, including:
        - Steam ID
        - Alias
        - Total games played
        - Games won and lost
        - Games played on each map
        - Games played in each format
        example: /players/<player_id>
        """
        try:
            # Query player
            player = session.query(Player).filter_by(id=player_id).first()
            if not player:
                return {"error": f"Player with id {player_id} not found."}, 404

            # Total games played
            total_games = (
                session.query(PlayerGame)
                .filter(PlayerGame.player_id == player_id)
                .count()
            )

            # Games won
            games_won = (
                session.query(PlayerGame)
                .join(Game, PlayerGame.game_id == Game.id)
                .filter(PlayerGame.player_id == player_id)
                .filter(
                    or_(
                        and_(PlayerGame.team == "red", Game.red_score > Game.blue_score),
                        and_(PlayerGame.team == "blue", Game.blue_score > Game.red_score)
                    )
                )
                .count()
            )

            # Games lost
            games_lost = (
                session.query(PlayerGame)
                .join(Game, PlayerGame.game_id == Game.id)
                .filter(PlayerGame.player_id == player_id)
                .filter(
                    or_(
                        and_(PlayerGame.team == "red", Game.red_score < Game.blue_score),
                        and_(PlayerGame.team == "blue", Game.blue_score < Game.red_score)
                    )
                )
                .count()
            )

            # Games tied
            games_tied = (
                session.query(PlayerGame)
                .join(Game, PlayerGame.game_id == Game.id)
                .filter(PlayerGame.player_id == player_id)
                .filter(Game.red_score == Game.blue_score)  # Condition for ties
                .count()
            )

            # Games played on each map
            maps = (
                session.query(Game.map, func.count(Game.id).label("game_count"))
                .join(PlayerGame, PlayerGame.game_id == Game.id)
                .filter(PlayerGame.player_id == player_id)
                .group_by(Game.map)
                .all()
            )

            # Games played in each format
            formats = (
                session.query(Game.format, func.count(Game.id).label("game_count"))
                .join(PlayerGame, PlayerGame.game_id == Game.id)
                .filter(PlayerGame.player_id == player_id)
                .group_by(Game.format)
                .all()
            )

            # Format the result
            result = {
                "id": str(player.id),
                "name": player.name,
                "games": {
                    "total": total_games,
                    "won": games_won,
                    "lost": games_lost,
                    "tied": games_tied,
                },
                "maps": {row.map: row.game_count for row in maps},
                "formats": {row.format: row.game_count for row in formats},
            }
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 500
                        
class PlayerAllies(Resource):
    def get(self, player_id):
        """
        get all players that a player has played on the same team with ordered by how many times
        """
        session = Session()
        try:
            result = get_playedwith(session, player_id, same_team=True)
            return result
        finally:
            session.close()

class PlayerEnemies(Resource):
    def get(self, player_id):
        """
        get all players that a player has played against ordered by how many times
        """
        session = Session()
        try:
            result = get_playedwith(session, player_id, same_team=False)
            return result
        finally:
            session.close()

# define endpoints
api.add_resource(PlayerInfo, "/players/<int:player_id>")
api.add_resource(PlayerAllies, "/players/<int:player_id>/allies")
api.add_resource(PlayerEnemies, "/players/<int:player_id>/enemies")
api.add_resource(SharedGames, "/shared/")
api.add_resource(Allies, "/shared/allies/")
api.add_resource(Enemies, "/shared/enemies/")
