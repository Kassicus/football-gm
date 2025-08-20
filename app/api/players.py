from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.connection import get_db
from ..database.models import Player, Team
from ..services.player_service import PlayerService
from ..services.player_evaluation import PlayerEvaluationService

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

@router.get("/{player_id}/evaluation")
def get_player_evaluation(player_id: int, db: Session = Depends(get_db)):
    """Get comprehensive player evaluation"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    evaluation_service = PlayerEvaluationService(db)
    
    # Calculate dynamic ratings
    calculated_overall = evaluation_service.calculate_overall_rating(player)
    calculated_potential = evaluation_service.calculate_potential(player)
    
    evaluation = {
        "player_id": player.id,
        "name": f"{player.first_name} {player.last_name}",
        "position": player.position,
        "current_ratings": {
            "overall": player.overall_rating,
            "potential": player.potential,
            "calculated_overall": calculated_overall,
            "calculated_potential": calculated_potential
        },
        "evaluation": {
            "grade": evaluation_service.get_position_grade(player),
            "development_trajectory": evaluation_service.get_development_trajectory(player),
            "injury_risk": evaluation_service.get_injury_risk(player)
        },
        "trade_value": evaluation_service.get_trade_value(player),
        "comparison": evaluation_service.get_comparison_data(player)
    }
    
    return evaluation

@router.get("/search/{search_term}")
def search_players(
    search_term: str,
    team_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Search players by name"""
    player_service = PlayerService(db)
    players = player_service.search_players(search_term, team_id)
    
    return [
        {
            "id": player.id,
            "name": f"{player.first_name} {player.last_name}",
            "position": player.position,
            "age": player.age,
            "overall_rating": player.overall_rating,
            "team_id": player.team_id
        }
        for player in players
    ]

@router.get("/positions/{position}/top")
def get_top_players_by_position(
    position: str,
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    """Get top players by position"""
    players = db.query(Player).filter(
        Player.position == position.upper(),
        Player.roster_status == "active"
    ).order_by(Player.overall_rating.desc()).limit(limit).all()
    
    return [
        {
            "id": player.id,
            "name": f"{player.first_name} {player.last_name}",
            "overall_rating": player.overall_rating,
            "age": player.age,
            "years_pro": player.years_pro,
            "team_id": player.team_id
        }
        for player in players
    ]

@router.get("/team/{team_id}/depth-chart")
def get_team_depth_chart(team_id: int, db: Session = Depends(get_db)):
    """Get team depth chart by position"""
    player_service = PlayerService(db)
    players = player_service.get_players_by_team(team_id, "active")
    
    # Group by position and sort by overall rating
    depth_chart = {}
    for player in players:
        pos = player.position
        if pos not in depth_chart:
            depth_chart[pos] = []
        
        depth_chart[pos].append({
            "id": player.id,
            "name": f"{player.first_name} {player.last_name}",
            "overall_rating": player.overall_rating,
            "age": player.age,
            "jersey_number": player.jersey_number
        })
    
    # Sort each position by overall rating
    for pos in depth_chart:
        depth_chart[pos].sort(key=lambda x: x["overall_rating"], reverse=True)
    
    return depth_chart
