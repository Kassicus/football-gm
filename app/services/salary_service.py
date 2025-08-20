from sqlalchemy.orm import Session
from ..database.models import Contract, Team

class SalaryService:
    def __init__(self, db: Session):
        self.db = db
        # 2024 NFL Salary Cap (will be configurable in future phases)
        self.salary_cap = 255400000
    
    def get_team_salary_cap_used(self, team_id: int) -> int:
        """Calculate total salary cap used by team"""
        contracts = self.db.query(Contract).filter(
            Contract.team_id == team_id,
            Contract.is_active == True
        ).all()
        
        total_used = sum(contract.year_1_salary for contract in contracts)
        return total_used
    
    def get_team_cap_space(self, team_id: int) -> int:
        """Calculate remaining cap space for team"""
        used = self.get_team_salary_cap_used(team_id)
        return self.salary_cap - used
    
    def get_team_cap_percentage(self, team_id: int) -> float:
        """Get percentage of salary cap used"""
        used = self.get_team_salary_cap_used(team_id)
        return (used / self.salary_cap) * 100
    
    def get_team_contracts(self, team_id: int) -> list[Contract]:
        """Get all active contracts for a team"""
        return self.db.query(Contract).filter(
            Contract.team_id == team_id,
            Contract.is_active == True
        ).all()
    
    def get_player_contract(self, player_id: int) -> Contract:
        """Get current contract for a player"""
        return self.db.query(Contract).filter(
            Contract.player_id == player_id,
            Contract.is_active == True
        ).first()
    
    def get_salary_cap(self) -> int:
        """Get current salary cap"""
        return self.salary_cap
