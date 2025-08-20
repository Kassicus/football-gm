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
    
    def get_team_roster(self, team_id: int, status: str = "active") -> list[Player]:
        """Get team roster by status"""
        return self.db.query(Player).filter(
            Player.team_id == team_id,
            Player.roster_status == status
        ).all()
    
    def get_team_by_abbreviation(self, abbreviation: str) -> Team:
        """Get team by abbreviation"""
        return self.db.query(Team).filter(Team.abbreviation == abbreviation).first()
