from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    bio = Column(Text)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tournaments = relationship("Tournament", back_populates="organizer")
    participations = relationship("Participation", back_populates="player")

class Tournament(Base):
    __tablename__ = "tournaments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    game = Column(String(50), nullable=False)  # e.g., "CS:GO", "Dota 2", "Valorant"
    description = Column(Text)
    max_teams = Column(Integer, default=16)
    prize_pool = Column(Integer, default=0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20), default="upcoming")  # upcoming, ongoing, completed
    organizer_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organizer = relationship("User", back_populates="tournaments")
    participations = relationship("Participation", back_populates="tournament")
    matches = relationship("Match", back_populates="tournament")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    tag = Column(String(10), unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    participations = relationship("Participation", back_populates="team")
    players = relationship("TeamPlayer", back_populates="team")

class TeamPlayer(Base):
    __tablename__ = "team_players"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_captain = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team", back_populates="players")
    user = relationship("User")

class Participation(Base):
    __tablename__ = "participations"
    
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    registered_at = Column(DateTime, default=datetime.utcnow)
    final_position = Column(Integer)
    
    tournament = relationship("Tournament", back_populates="participations")
    team = relationship("Team", back_populates="participations")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    round = Column(Integer, default=1)
    team1_id = Column(Integer, ForeignKey("teams.id"))
    team2_id = Column(Integer, ForeignKey("teams.id"))
    score1 = Column(Integer, default=0)
    score2 = Column(Integer, default=0)
    winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    match_date = Column(DateTime)
    status = Column(String(20), default="scheduled")  # scheduled, ongoing, completed
    
    tournament = relationship("Tournament", back_populates="matches")