"""
model classes for use elsewhere
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)

    # Relationships
    games = relationship("PlayerGame", back_populates="player")

class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    logstf_id = Column(Integer, nullable=False)
    map = Column(String, nullable=False)
    format = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)
    red_score = Column(Integer, nullable=False)
    blue_score = Column(Integer, nullable=False)

    # Relationships
    players = relationship("PlayerGame", back_populates="game")

class PlayerGame(Base):
    __tablename__ = 'player_games'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    team = Column(String, nullable=False)

    # Relationships
    player = relationship("Player", back_populates="games")
    game = relationship("Game", back_populates="players")

