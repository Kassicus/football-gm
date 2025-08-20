from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.models import Player, Team, Position

class PlayerService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_players_by_team(self, team_id: int, status: str = "active") -> List[Player]:
        """Get all players for a specific team"""
        return self.db.query(Player).filter(
            Player.team_id == team_id,
            Player.roster_status == status
        ).all()
    
    def get_players_by_position(self, position: str, team_id: Optional[int] = None) -> List[Player]:
        """Get players by position, optionally filtered by team"""
        query = self.db.query(Player).filter(Player.position == position.upper())
        if team_id:
            query = query.filter(Player.team_id == team_id)
        return query.all()
    
    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Get player by ID"""
        return self.db.query(Player).filter(Player.id == player_id).first()
    
    def search_players(self, search_term: str, team_id: Optional[int] = None) -> List[Player]:
        """Search players by name"""
        query = self.db.query(Player).filter(
            (Player.first_name.ilike(f"%{search_term}%")) |
            (Player.last_name.ilike(f"%{search_term}%"))
        )
        if team_id:
            query = query.filter(Player.team_id == team_id)
        return query.all()
    
    def get_position_info(self, position_code: str) -> Optional[Position]:
        """Get position information by code"""
        return self.db.query(Position).filter(Position.code == position_code.upper()).first()
    
    def get_all_positions(self) -> List[Position]:
        """Get all positions"""
        return self.db.query(Position).all()
    
    def update_player_status(self, player_id: int, new_status: str) -> bool:
        """Update player roster status"""
        player = self.get_player_by_id(player_id)
        if player:
            player.roster_status = new_status
            self.db.commit()
            return True
        return False
