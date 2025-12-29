from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    bio: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Tournament Schemas
class TournamentBase(BaseModel):
    name: str
    game: str
    description: Optional[str] = None
    max_teams: int = 16
    prize_pool: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TournamentCreate(TournamentBase):
    pass

class Tournament(TournamentBase):
    id: int
    status: str
    organizer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TournamentWithOrganizer(Tournament):
    organizer: User

# Team Schemas
class TeamBase(BaseModel):
    name: str
    tag: Optional[str] = None
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Match Schemas
class MatchBase(BaseModel):
    tournament_id: int
    round: int = 1
    team1_id: int
    team2_id: int
    score1: int = 0
    score2: int = 0
    match_date: Optional[datetime] = None

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: int
    winner_id: Optional[int] = None
    status: str
    
    class Config:
        from_attributes = True

class MatchWithTeams(Match):
    team1: Team
    team2: Team
    winner: Optional[Team] = None

# Participation Schemas
class ParticipationBase(BaseModel):
    tournament_id: int
    team_id: int

class ParticipationCreate(ParticipationBase):
    pass

class Participation(ParticipationBase):
    id: int
    registered_at: datetime
    final_position: Optional[int] = None
    
    class Config:
        from_attributes = True

class ParticipationWithDetails(Participation):
    tournament: Tournament
    team: Team