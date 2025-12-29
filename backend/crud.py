from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
import schemas
from auth import get_password_hash, verify_password
from typing import Optional, List

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Tournament CRUD
def get_tournament(db: Session, tournament_id: int):
    return db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()

def get_tournaments(db: Session, skip: int = 0, limit: int = 100, game: Optional[str] = None):
    query = db.query(models.Tournament)
    if game:
        query = query.filter(models.Tournament.game == game)
    return query.offset(skip).limit(limit).all()

def create_tournament(db: Session, tournament: schemas.TournamentCreate, organizer_id: int):
    db_tournament = models.Tournament(**tournament.dict(), organizer_id=organizer_id)
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament

def update_tournament(db: Session, tournament_id: int, tournament_update: dict):
    db_tournament = get_tournament(db, tournament_id)
    if not db_tournament:
        return None
    
    for key, value in tournament_update.items():
        setattr(db_tournament, key, value)
    
    db.commit()
    db.refresh(db_tournament)
    return db_tournament

def delete_tournament(db: Session, tournament_id: int):
    db_tournament = get_tournament(db, tournament_id)
    if db_tournament:
        db.delete(db_tournament)
        db.commit()
    return db_tournament

# Team CRUD
def get_team(db: Session, team_id: int):
    return db.query(models.Team).filter(models.Team.id == team_id).first()

def get_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Team).offset(skip).limit(limit).all()

def create_team(db: Session, team: schemas.TeamCreate):
    db_team = models.Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

# Match CRUD
def get_match(db: Session, match_id: int):
    return db.query(models.Match).filter(models.Match.id == match_id).first()

def get_tournament_matches(db: Session, tournament_id: int):
    return db.query(models.Match).filter(models.Match.tournament_id == tournament_id).all()

def create_match(db: Session, match: schemas.MatchCreate):
    db_match = models.Match(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def update_match_score(db: Session, match_id: int, score1: int, score2: int, winner_id: Optional[int] = None):
    db_match = get_match(db, match_id)
    if not db_match:
        return None
    
    db_match.score1 = score1
    db_match.score2 = score2
    db_match.winner_id = winner_id
    db_match.status = "completed" if winner_id else "ongoing"
    
    db.commit()
    db.refresh(db_match)
    return db_match

# Participation CRUD
def register_team(db: Session, participation: schemas.ParticipationCreate):
    # Check if team is already registered
    existing = db.query(models.Participation).filter(
        models.Participation.tournament_id == participation.tournament_id,
        models.Participation.team_id == participation.team_id
    ).first()
    
    if existing:
        return None
    
    db_participation = models.Participation(**participation.dict())
    db.add(db_participation)
    db.commit()
    db.refresh(db_participation)
    return db_participation

def get_tournament_participants(db: Session, tournament_id: int):
    return db.query(models.Participation).filter(
        models.Participation.tournament_id == tournament_id
    ).all()