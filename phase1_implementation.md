# Phase 1 Implementation Guide - NFL GM Simulator

## Overview
Phase 1 establishes the foundation of your NFL GM simulator with database schema, basic API endpoints, and core frontend pages. This document provides step-by-step implementation details.

---

## Project Setup

### 1. Initial Project Structure
```
nfl_gm_simulator/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py    # Database connection
│   │   ├── models.py        # SQLAlchemy models
│   │   └── init_db.py       # Database initialization
│   ├── api/
│   │   ├── __init__.py
│   │   ├── teams.py         # Team endpoints
│   │   ├── players.py       # Player endpoints
│   │   ├── roster.py        # Roster management
│   │   └── salary_cap.py    # Salary cap endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── team_service.py  # Business logic
│   │   ├── player_service.py
│   │   └── salary_service.py
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── dashboard.html
│       ├── roster.html
│       └── salary_cap.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
├── data/
│   ├── teams.json           # Initial team data
│   ├── players.json         # Initial player data
│   └── positions.json       # Position definitions
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_api.py
├── requirements.txt
└── README.md
```

### 2. Requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
jinja2==3.1.2
python-multipart==0.0.6
htmx==0.3.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

---

## Database Schema & Models

### 1. Core Database Models (`app/database/models.py`)

#### Teams Table
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    abbreviation = Column(String(3), unique=True, nullable=False)
    conference = Column(String(3), nullable=False)  # AFC/NFC
    division = Column(String(10), nullable=False)   # North/South/East/West
    
    # Colors for UI
    primary_color = Column(String(7))    # Hex color
    secondary_color = Column(String(7))  # Hex color
    
    # Stadium info
    stadium_name = Column(String(100))
    capacity = Column(Integer)
    
    # Metadata
    founded_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Players Table
```python
class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    
    # Basic Info
    position = Column(String(5), nullable=False)  # QB, RB, WR, etc.
    jersey_number = Column(Integer)
    age = Column(Integer)
    height = Column(Integer)  # Inches
    weight = Column(Integer)  # Pounds
    
    # Career Info
    years_pro = Column(Integer, default=0)
    college = Column(String(100))
    draft_year = Column(Integer)
    draft_round = Column(Integer)
    draft_pick = Column(Integer)
    
    # Team Association
    team_id = Column(Integer, ForeignKey("teams.id"))
    roster_status = Column(String(20))  # active, practice_squad, injured_reserve, suspended
    
    # Attributes (0-100 scale)
    overall_rating = Column(Integer, default=50)
    potential = Column(Integer, default=50)
    
    # Physical Attributes
    speed = Column(Integer, default=50)
    strength = Column(Integer, default=50)
    agility = Column(Integer, default=50)
    
    # Mental Attributes  
    football_iq = Column(Integer, default=50)
    leadership = Column(Integer, default=50)
    work_ethic = Column(Integer, default=50)
    
    # Position-specific skills (will expand based on position)
    skill_1 = Column(Integer, default=50)  # e.g., Accuracy for QB
    skill_2 = Column(Integer, default=50)  # e.g., Arm Strength for QB
    skill_3 = Column(Integer, default=50)  # e.g., Pocket Presence for QB
    
    # Contract & Status
    injury_status = Column(String(50), default="healthy")
    injury_prone = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Contracts Table
```python
class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Contract Terms
    total_value = Column(Integer)  # Total contract value in dollars
    guaranteed_money = Column(Integer, default=0)
    years = Column(Integer, nullable=False)
    
    # Annual Breakdown
    year_1_salary = Column(Integer, default=0)
    year_2_salary = Column(Integer, default=0)
    year_3_salary = Column(Integer, default=0)
    year_4_salary = Column(Integer, default=0)
    year_5_salary = Column(Integer, default=0)
    
    # Bonuses
    signing_bonus = Column(Integer, default=0)
    roster_bonus = Column(Integer, default=0)
    
    # Contract Status
    contract_type = Column(String(20))  # rookie, veteran, extension, franchise_tag
    is_active = Column(Boolean, default=True)
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Positions Table
```python
class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(5), unique=True, nullable=False)  # QB, RB, WR, etc.
    name = Column(String(50), nullable=False)  # Quarterback, Running Back, etc.
    position_group = Column(String(20))  # offense, defense, special_teams
    
    # Roster Limits
    max_roster = Column(Integer)  # Max players at position on roster
    typical_roster = Column(Integer)  # Typical number carried
    
    # Key Attributes (for player evaluation)
    key_attribute_1 = Column(String(20))  # e.g., "speed" for RB
    key_attribute_2 = Column(String(20))  # e.g., "strength" for RB
    key_attribute_3 = Column(String(20))  # e.g., "agility" for RB
```

### 2. Database Connection (`app/database/connection.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

DATABASE_URL = "sqlite:///./nfl_gm.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL logging during development
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3. Database Initialization (`app/database/init_db.py`)
```python
import json
from sqlalchemy.orm import Session
from .connection import SessionLocal, create_tables
from .models import Team, Player, Position, Contract

def init_database():
    """Initialize database with default data"""
    create_tables()
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Team).first():
            print("Database already initialized")
            return
        
        # Load and insert teams
        with open('data/teams.json', 'r') as f:
            teams_data = json.load(f)
        
        for team_data in teams_data:
            team = Team(**team_data)
            db.add(team)
        
        # Load and insert positions
        with open('data/positions.json', 'r') as f:
            positions_data = json.load(f)
        
        for pos_data in positions_data:
            position = Position(**pos_data)
            db.add(position)
        
        db.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
```

---

## API Implementation

### 1. Main FastAPI App (`app/main.py`)
```python
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from .api import teams, players, roster, salary_cap
from .database.init_db import init_database

app = FastAPI(title="NFL GM Simulator", version="1.0.0")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(roster.router, prefix="/api/roster", tags=["roster"])
app.include_router(salary_cap.router, prefix="/api/salary-cap", tags=["salary-cap"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/roster", response_class=HTMLResponse)
async def roster_page(request: Request):
    """Roster management page"""
    return templates.TemplateResponse("roster.html", {"request": request})

@app.get("/salary-cap", response_class=HTMLResponse)
async def salary_cap_page(request: Request):
    """Salary cap management page"""
    return templates.TemplateResponse("salary_cap.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### 2. Teams API (`app/api/teams.py`)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.connection import get_db
from ..database.models import Team
from ..services.team_service import TeamService

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_all_teams(db: Session = Depends(get_db)):
    """Get all NFL teams"""
    teams = db.query(Team).all()
    return [
        {
            "id": team.id,
            "name": team.name,
            "city": team.city,
            "abbreviation": team.abbreviation,
            "conference": team.conference,
            "division": team.division,
            "colors": {
                "primary": team.primary_color,
                "secondary": team.secondary_color
            }
        }
        for team in teams
    ]

@router.get("/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get specific team details"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team_service = TeamService(db)
    roster_count = team_service.get_roster_count(team_id)
    salary_cap_used = team_service.get_salary_cap_used(team_id)
    
    return {
        "id": team.id,
        "name": team.name,
        "city": team.city,
        "abbreviation": team.abbreviation,
        "conference": team.conference,
        "division": team.division,
        "stadium": team.stadium_name,
        "capacity": team.capacity,
        "roster_count": roster_count,
        "salary_cap_used": salary_cap_used
    }
```

### 3. Players API (`app/api/players.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.connection import get_db
from ..database.models import Player, Team
from ..services.player_service import PlayerService

router = APIRouter()

@router.get("/")
def get_players(
    team_id: Optional[int] = Query(None),
    position: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get players with filtering options"""
    query = db.query(Player)
    
    if team_id:
        query = query.filter(Player.team_id == team_id)
    if position:
        query = query.filter(Player.position == position.upper())
    if status:
        query = query.filter(Player.roster_status == status)
    
    players = query.offset(offset).limit(limit).all()
    
    return [
        {
            "id": player.id,
            "name": f"{player.first_name} {player.last_name}",
            "position": player.position,
            "jersey_number": player.jersey_number,
            "age": player.age,
            "overall_rating": player.overall_rating,
            "team_id": player.team_id,
            "roster_status": player.roster_status
        }
        for player in players
    ]

@router.get("/{player_id}")
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get detailed player information"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    team = db.query(Team).filter(Team.id == player.team_id).first()
    
    return {
        "id": player.id,
        "first_name": player.first_name,
        "last_name": player.last_name,
        "position": player.position,
        "jersey_number": player.jersey_number,
        "age": player.age,
        "height": player.height,
        "weight": player.weight,
        "years_pro": player.years_pro,
        "college": player.college,
        "team": team.name if team else None,
        "ratings": {
            "overall": player.overall_rating,
            "potential": player.potential,
            "speed": player.speed,
            "strength": player.strength,
            "agility": player.agility,
            "football_iq": player.football_iq,
            "leadership": player.leadership,
            "work_ethic": player.work_ethic
        },
        "status": {
            "roster_status": player.roster_status,
            "injury_status": player.injury_status,
            "injury_prone": player.injury_prone
        }
    }
```

---

## Services Layer

### 1. Team Service (`app/services/team_service.py`)
```python
from sqlalchemy.orm import Session
from ..database.models import Team, Player, Contract

class TeamService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_roster_count(self, team_id: int) -> int:
        """Get current roster count for team"""
        return self.db.query(Player).filter(
            Player.team_id == team_id,
            Player.roster_status == "active"
        ).count()
    
    def get_salary_cap_used(self, team_id: int) -> int:
        """Calculate total salary cap used by team"""
        contracts = self.db.query(Contract).filter(
            Contract.team_id == team_id,
            Contract.is_active == True
        ).all()
        
        # Simple calculation - just current year salary
        # Will be expanded in Phase 3
        total_used = sum(contract.year_1_salary for contract in contracts)
        return total_used
    
    def get_team_by_id(self, team_id: int) -> Team:
        """Get team by ID"""
        return self.db.query(Team).filter(Team.id == team_id).first()
    
    def get_all_teams(self) -> list[Team]:
        """Get all teams"""
        return self.db.query(Team).all()
```

---

## Frontend Templates

### 1. Base Template (`app/templates/base.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}NFL GM Simulator{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/styles.css">
    <script src="https://unpkg.com/htmx.org@1.9.8"></script>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <h1 class="nav-title">NFL GM Simulator</h1>
            <ul class="nav-menu">
                <li><a href="/" class="nav-link">Dashboard</a></li>
                <li><a href="/roster" class="nav-link">Roster</a></li>
                <li><a href="/salary-cap" class="nav-link">Salary Cap</a></li>
            </ul>
        </div>
    </nav>

    <main class="main-content">
        {% block content %}{% endblock %}
    </main>

    <script src="/static/js/main.js"></script>
</body>
</html>
```

### 2. Dashboard Template (`app/templates/dashboard.html`)
```html
{% extends "base.html" %}

{% block title %}Dashboard - NFL GM Simulator{% endblock %}

{% block content %}
<div class="dashboard">
    <h2>Team Dashboard</h2>
    
    <div class="dashboard-grid">
        <!-- Team Overview Card -->
        <div class="card" hx-get="/api/teams/1" hx-trigger="load" hx-target="#team-info">
            <h3>Team Overview</h3>
            <div id="team-info">Loading...</div>
        </div>
        
        <!-- Roster Summary Card -->
        <div class="card">
            <h3>Roster Summary</h3>
            <div hx-get="/api/players?team_id=1&limit=5" hx-trigger="load" hx-target="#roster-summary">
                <div id="roster-summary">Loading...</div>
            </div>
        </div>
        
        <!-- Salary Cap Card -->
        <div class="card">
            <h3>Salary Cap</h3>
            <div class="cap-info">
                <p>Cap Space: <span class="money" hx-get="/api/salary-cap/remaining" hx-trigger="load">--</span></p>
                <p>Cap Used: <span class="money" hx-get="/api/salary-cap/used" hx-trigger="load">--</span></p>
            </div>
        </div>
        
        <!-- Recent Transactions -->
        <div class="card">
            <h3>Recent Transactions</h3>
            <div class="transactions-list">
                <p>No recent transactions</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## Initial Data Files

### 1. Teams Data (`data/teams.json`)
```json
[
    {
        "name": "Ravens",
        "city": "Baltimore",
        "abbreviation": "BAL",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#241773",
        "secondary_color": "#000000",
        "stadium_name": "M&T Bank Stadium",
        "capacity": 71008,
        "founded_year": 1996
    },
    {
        "name": "Bengals",
        "city": "Cincinnati",
        "abbreviation": "CIN",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#FB4F14",
        "secondary_color": "#000000",
        "stadium_name": "Paycor Stadium",
        "capacity": 65515,
        "founded_year": 1968
    }
]
```

### 2. Positions Data (`data/positions.json`)
```json
[
    {
        "code": "QB",
        "name": "Quarterback",
        "position_group": "offense",
        "max_roster": 4,
        "typical_roster": 3,
        "key_attribute_1": "football_iq",
        "key_attribute_2": "skill_1",
        "key_attribute_3": "leadership"
    },
    {
        "code": "RB",
        "name": "Running Back",
        "position_group": "offense",
        "max_roster": 6,
        "typical_roster": 4,
        "key_attribute_1": "speed",
        "key_attribute_2": "agility",
        "key_attribute_3": "strength"
    }
]
```

---

## Testing Setup

### 1. Basic Model Tests (`tests/test_models.py`)
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Team, Player

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_team(db):
    team = Team(
        name="Test Team",
        city="Test City",
        abbreviation="TST",
        conference="AFC",
        division="North"
    )
    db.add(team)
    db.commit()
    
    assert team.id is not None
    assert team.name == "Test Team"

def test_create_player(db):
    # First create a team
    team = Team(name="Test Team", city="Test City", abbreviation="TST", conference="AFC", division="North")
    db.add(team)
    db.commit()
    
    player = Player(
        first_name="John",
        last_name="Doe",
        position="QB",
        age=25,
        team_id=team.id,
        overall_rating=80
    )
    db.add(player)
    db.commit()
    
    assert player.id is not None
    assert player.first_name == "John"
    assert player.team_id == team.id
```

---

## Next Steps Checklist

### Week 1: Project Setup
- [ ] Create project directory structure
- [ ] Set up virtual environment and install dependencies
- [ ] Initialize git repository
- [ ] Create basic FastAPI app structure

### Week 2: Database Foundation
- [ ] Implement all database models
- [ ] Create database connection and initialization
- [ ] Set up initial data files (teams, positions)
- [ ] Test database operations

### Week 3: Basic API Endpoints
- [ ] Implement teams API endpoints
- [ ] Implement players API endpoints
- [ ] Create basic service layer
- [ ] Test API functionality

### Week 4: Frontend Foundation
- [ ] Create base HTML templates
- [ ] Set up basic CSS styling
- [ ] Implement dashboard page
- [ ] Add HTMX for dynamic updates

### Week 5: Integration & Testing
- [ ] Connect frontend to API endpoints
- [ ] Add basic error handling
- [ ] Write unit tests
- [ ] Performance testing with sample data

### Week 6: Polish & Documentation
- [ ] Refine UI/UX
- [ ] Add loading states and error messages
- [ ] Document API endpoints
- [ ] Prepare for Phase 2

---

## Development Tips

1. **Start Simple**: Focus on getting basic functionality working before adding complexity
2. **Test Early**: Set up testing framework from the beginning
3. **Use SQLite Browser**: Install DB Browser for SQLite to inspect your database during development
4. **API Testing**: Use FastAPI's automatic docs at `/docs` to test endpoints
5. **Version Control**: Commit frequently with descriptive messages
6. **Performance**: Add database indexes as needed for common queries

This Phase 1 implementation will give you a solid foundation to build upon in subsequent phases!