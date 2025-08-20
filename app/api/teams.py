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

@router.get("/{team_id}/roster")
def get_team_roster(team_id: int, status: str = "active", db: Session = Depends(get_db)):
    """Get team roster"""
    team_service = TeamService(db)
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    players = team_service.get_team_roster(team_id, status)
    return {
        "team": {
            "id": team.id,
            "name": team.name,
            "abbreviation": team.abbreviation
        },
        "roster": [
            {
                "id": player.id,
                "name": f"{player.first_name} {player.last_name}",
                "position": player.position,
                "jersey_number": player.jersey_number,
                "age": player.age,
                "overall_rating": player.overall_rating,
                "roster_status": player.roster_status
            }
            for player in players
        ]
    }
