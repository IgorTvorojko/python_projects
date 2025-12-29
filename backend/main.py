from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import uvicorn

import crud, models, schemas, auth
from database import SessionLocal, engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cyber Tournament API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    return current_user

# Tournament endpoints
@app.post("/tournaments/", response_model=schemas.Tournament)
def create_tournament(
    tournament: schemas.TournamentCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.create_tournament(db=db, tournament=tournament, organizer_id=current_user.id)

@app.get("/tournaments/", response_model=List[schemas.Tournament])
def read_tournaments(
    skip: int = 0,
    limit: int = 100,
    game: str = None,
    db: Session = Depends(get_db)
):
    tournaments = crud.get_tournaments(db, skip=skip, limit=limit, game=game)
    return tournaments

@app.get("/tournaments/{tournament_id}", response_model=schemas.Tournament)
def read_tournament(tournament_id: int, db: Session = Depends(get_db)):
    db_tournament = crud.get_tournament(db, tournament_id=tournament_id)
    if db_tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return db_tournament

@app.put("/tournaments/{tournament_id}", response_model=schemas.Tournament)
def update_tournament(
    tournament_id: int,
    tournament_update: schemas.TournamentCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if user is the organizer
    tournament = crud.get_tournament(db, tournament_id)
    if not tournament or tournament.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud.update_tournament(db, tournament_id, tournament_update.dict())

@app.delete("/tournaments/{tournament_id}")
def delete_tournament(
    tournament_id: int,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if user is the organizer
    tournament = crud.get_tournament(db, tournament_id)
    if not tournament or tournament.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    crud.delete_tournament(db, tournament_id)
    return {"message": "Tournament deleted successfully"}

# Team endpoints
@app.post("/teams/", response_model=schemas.Team)
def create_team(
    team: schemas.TeamCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.create_team(db=db, team=team)

@app.get("/teams/", response_model=List[schemas.Team])
def read_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teams = crud.get_teams(db, skip=skip, limit=limit)
    return teams

# Match endpoints
@app.post("/matches/", response_model=schemas.Match)
def create_match(
    match: schemas.MatchCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if user has permission (tournament organizer)
    tournament = crud.get_tournament(db, match.tournament_id)
    if not tournament or tournament.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud.create_match(db=db, match=match)

@app.put("/matches/{match_id}/score")
def update_match_score(
    match_id: int,
    score1: int,
    score2: int,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    match = crud.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Check if user has permission
    tournament = crud.get_tournament(db, match.tournament_id)
    if not tournament or tournament.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    winner_id = match.team1_id if score1 > score2 else match.team2_id if score2 > score1 else None
    return crud.update_match_score(db, match_id, score1, score2, winner_id)

# Participation endpoints
@app.post("/participations/", response_model=schemas.Participation)
def register_for_tournament(
    participation: schemas.ParticipationCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    result = crud.register_team(db, participation)
    if not result:
        raise HTTPException(status_code=400, detail="Team already registered")
    return result

@app.get("/tournaments/{tournament_id}/participants")
def get_tournament_participants(tournament_id: int, db: Session = Depends(get_db)):
    return crud.get_tournament_participants(db, tournament_id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)