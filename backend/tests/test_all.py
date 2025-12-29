import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from database import Base
import models
import schemas
import crud
from auth import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Test data
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
}

test_tournament = {
    "name": "Test Tournament",
    "game": "CS:GO",
    "description": "Test tournament description",
    "max_teams": 8,
    "prize_pool": 1000
}

# Unit tests
def test_create_user():
    db = TestingSessionLocal()
    user_data = schemas.UserCreate(**test_user)
    user = crud.create_user(db, user_data)
    assert user.username == test_user["username"]
    assert user.email == test_user["email"]
    db.close()

def test_authenticate_user():
    db = TestingSessionLocal()
    user_data = schemas.UserCreate(**test_user)
    user = crud.create_user(db, user_data)
    
    authenticated = crud.authenticate_user(db, test_user["username"], test_user["password"])
    assert authenticated is not False
    assert authenticated.username == test_user["username"]
    
    wrong_auth = crud.authenticate_user(db, test_user["username"], "wrongpass")
    assert wrong_auth is False
    db.close()

def test_create_tournament():
    db = TestingSessionLocal()
    # Create user first
    user_data = schemas.UserCreate(**test_user)
    user = crud.create_user(db, user_data)
    
    tournament_data = schemas.TournamentCreate(**test_tournament)
    tournament = crud.create_tournament(db, tournament_data, user.id)
    
    assert tournament.name == test_tournament["name"]
    assert tournament.organizer_id == user.id
    db.close()

# Integration tests
class TestAuth:
    def test_register(self):
        response = client.post("/register", json=test_user)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user["username"]
        assert "password" not in data
    
    def test_login(self):
        # First register
        client.post("/register", json=test_user)
        
        response = client.post("/token", data={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_protected_endpoint(self):
        # Register and login
        client.post("/register", json=test_user)
        login_response = client.post("/token", data={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user["username"]

class TestTournaments:
    def setup_method(self):
        # Register and login
        client.post("/register", json=test_user)
        login_response = client.post("/token", data={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_tournament(self):
        response = client.post("/tournaments/", json=test_tournament, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_tournament["name"]
        assert data["game"] == test_tournament["game"]
        self.tournament_id = data["id"]
    
    def test_get_tournaments(self):
        response = client.get("/tournaments/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_single_tournament(self):
        # First create a tournament
        create_response = client.post("/tournaments/", json=test_tournament, headers=self.headers)
        tournament_id = create_response.json()["id"]
        
        response = client.get(f"/tournaments/{tournament_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tournament_id

class TestTeams:
    def setup_method(self):
        client.post("/register", json=test_user)
        login_response = client.post("/token", data={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_team(self):
        team_data = {
            "name": "Test Team",
            "tag": "TT",
            "description": "Test team description"
        }
        response = client.post("/teams/", json=team_data, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == team_data["name"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])