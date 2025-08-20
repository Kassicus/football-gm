from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from ..database.models import Contract, Player, Team
from ..services.salary_cap_service import SalaryCapService
from ..services.player_evaluation import PlayerEvaluationService
from datetime import datetime, timedelta
import random

class ContractService:
    def __init__(self, db: Session):
        self.db = db
        self.salary_cap_service = SalaryCapService(db)
        self.player_evaluation_service = PlayerEvaluationService(db)
    
    def get_player_contract(self, player_id: int) -> Optional[Contract]:
        """Get current active contract for a player"""
        return self.db.query(Contract).filter(
            Contract.player_id == player_id,
            Contract.is_active == True
        ).first()
    
    def get_player_contract_history(self, player_id: int) -> List[Contract]:
        """Get all contracts for a player (active and inactive)"""
        return self.db.query(Contract).filter(
            Contract.player_id == player_id
        ).order_by(Contract.start_date.desc()).all()
    
    def negotiate_contract_extension(self, player_id: int, team_id: int, 
                                   base_salary: int, years: int,
                                   signing_bonus: int = 0) -> Dict[str, any]:
        """Negotiate a contract extension with a player"""
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"error": "Player not found"}
        
        # Check if player already has an active contract
        existing_contract = self.get_player_contract(player_id)
        if existing_contract and existing_contract.team_id != team_id:
            return {"error": "Player is under contract with another team"}
        
        # Calculate market value based on player attributes
        market_value = self.calculate_market_value(player, base_salary, years)
        
        # Determine if player accepts the offer
        acceptance_chance = self.calculate_acceptance_chance(player, market_value, base_salary)
        accepted = random.random() < acceptance_chance
        
        if not accepted:
            return {
                "success": False,
                "message": "Player rejected the contract offer",
                "market_value": market_value,
                "acceptance_chance": round(acceptance_chance * 100, 1)
            }
        
        # Create new contract
        if existing_contract:
            # Extend existing contract
            new_contract = self.salary_cap_service.create_veteran_contract(
                player, team_id, base_salary, years, signing_bonus
            )
            # Deactivate old contract
            existing_contract.is_active = False
        else:
            # Create new contract
            new_contract = self.salary_cap_service.create_veteran_contract(
                player, team_id, base_salary, years, signing_bonus
            )
        
        # Save to database
        self.db.add(new_contract)
        self.db.commit()
        
        return {
            "success": True,
            "message": "Contract extension signed successfully",
            "contract_id": new_contract.id,
            "total_value": new_contract.total_value,
            "cap_hit_year_1": new_contract.year_1_cap_hit
        }
    
    def calculate_market_value(self, player: Player, base_salary: int, years: int) -> int:
        """Calculate market value for a player based on attributes and position"""
        # Base market value from overall rating
        base_value = player.overall_rating * 1000000  # $1M per overall point
        
        # Position multipliers
        position_multipliers = {
            'QB': 1.5, 'DE': 1.3, 'WR': 1.2, 'CB': 1.1,
            'LT': 1.2, 'TE': 1.0, 'RB': 0.9, 'ILB': 0.9
        }
        position_multiplier = position_multipliers.get(player.position, 1.0)
        
        # Age adjustment
        if player.age <= 25:
            age_multiplier = 1.3
        elif player.age <= 28:
            age_multiplier = 1.1
        elif player.age <= 31:
            age_multiplier = 1.0
        elif player.age <= 34:
            age_multiplier = 0.8
        else:
            age_multiplier = 0.6
        
        # Years pro adjustment
        if player.years_pro <= 3:
            experience_multiplier = 1.2
        elif player.years_pro <= 6:
            experience_multiplier = 1.0
        else:
            experience_multiplier = 0.9
        
        market_value = int(base_value * position_multiplier * age_multiplier * experience_multiplier)
        return market_value
    
    def calculate_acceptance_chance(self, player: Player, market_value: int, offered_salary: int) -> float:
        """Calculate the chance a player accepts a contract offer"""
        # Base acceptance chance
        base_chance = 0.5
        
        # Salary comparison factor
        if offered_salary >= market_value:
            salary_factor = 1.0
        else:
            # Decrease chance as offer gets further below market value
            salary_ratio = offered_salary / market_value
            salary_factor = max(0.1, salary_ratio)
        
        # Player loyalty factor (if they've been with the team)
        loyalty_factor = 1.0
        existing_contract = self.get_player_contract(player.id)
        if existing_contract and existing_contract.team_id == player.team_id:
            loyalty_factor = 1.2
        
        # Work ethic factor
        work_ethic_factor = 0.8 + (player.work_ethic / 100) * 0.4
        
        # Calculate final acceptance chance
        acceptance_chance = base_chance * salary_factor * loyalty_factor * work_ethic_factor
        return min(0.95, max(0.05, acceptance_chance))  # Clamp between 5% and 95%
    
    def restructure_contract(self, contract_id: int, restructure_amount: int) -> Dict[str, any]:
        """Restructure an existing contract to create cap space"""
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return {"error": "Contract not found"}
        
        if not contract.is_active:
            return {"error": "Contract is not active"}
        
        # Use salary cap service to restructure
        result = self.salary_cap_service.restructure_contract(contract, restructure_amount)
        
        if result.get("success"):
            self.db.commit()
        
        return result
    
    def release_player(self, contract_id: int, post_june_1: bool = False) -> Dict[str, any]:
        """Release a player and calculate dead money"""
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return {"error": "Contract not found"}
        
        # Use salary cap service to release player
        result = self.salary_cap_service.release_player(contract, post_june_1)
        
        if result.get("success"):
            self.db.commit()
        
        return result
    
    def franchise_tag_player(self, player_id: int, team_id: int) -> Dict[str, any]:
        """Apply franchise tag to a player"""
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"error": "Player not found"}
        
        # Check if player already has an active contract
        existing_contract = self.get_player_contract(player_id)
        if existing_contract:
            return {"error": "Player is already under contract"}
        
        # Calculate franchise tag amount (average of top 5 salaries at position)
        franchise_tag_amount = self.calculate_franchise_tag_amount(player.position)
        
        # Create franchise tag contract (1 year)
        contract = Contract(
            player_id=player_id,
            team_id=team_id,
            total_value=franchise_tag_amount,
            guaranteed_money=franchise_tag_amount,
            years=1,
            year_1_salary=franchise_tag_amount,
            contract_type="franchise_tag",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=365),
            is_active=True
        )
        
        # Calculate cap hit
        self.salary_cap_service.calculate_contract_cap_hits(contract)
        
        # Save to database
        self.db.add(contract)
        self.db.commit()
        
        return {
            "success": True,
            "message": "Franchise tag applied successfully",
            "franchise_tag_amount": franchise_tag_amount,
            "cap_hit": contract.year_1_cap_hit
        }
    
    def calculate_franchise_tag_amount(self, position: str) -> int:
        """Calculate franchise tag amount for a position"""
        # Simplified franchise tag calculation
        # In reality, this would be based on the average of top 5 salaries at the position
        
        base_franchise_tag = 20000000  # $20M base
        
        position_multipliers = {
            'QB': 2.0, 'DE': 1.5, 'WR': 1.3, 'CB': 1.2,
            'LT': 1.4, 'TE': 1.0, 'RB': 0.8, 'ILB': 0.9
        }
        
        multiplier = position_multipliers.get(position, 1.0)
        return int(base_franchise_tag * multiplier)
    
    def get_contract_analysis(self, contract_id: int) -> Dict[str, any]:
        """Get detailed analysis of a contract"""
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return {"error": "Contract not found"}
        
        player = self.db.query(Player).filter(Player.id == contract.player_id).first()
        if not player:
            return {"error": "Player not found"}
        
        # Calculate cap hits if not already done
        if not contract.year_1_cap_hit:
            self.salary_cap_service.calculate_contract_cap_hits(contract)
        
        # Get contract analysis
        analysis = {
            "contract_id": contract.id,
            "player_name": f"{player.first_name} {player.last_name}",
            "position": player.position,
            "team_id": contract.team_id,
            "contract_type": contract.contract_type,
            "total_value": contract.total_value,
            "guaranteed_money": contract.guaranteed_money,
            "years": contract.years,
            "annual_breakdown": {},
            "cap_analysis": {},
            "dead_money_analysis": {}
        }
        
        # Annual breakdown
        for year in range(1, contract.years + 1):
            salary = getattr(contract, f"year_{year}_salary", 0)
            cap_hit = getattr(contract, f"year_{year}_cap_hit", 0)
            dead_money = getattr(contract, f"dead_money_year_{year}", 0)
            
            analysis["annual_breakdown"][f"year_{year}"] = {
                "base_salary": salary,
                "cap_hit": cap_hit,
                "dead_money": dead_money
            }
        
        # Cap analysis
        total_cap_hit = sum(analysis["annual_breakdown"][f"year_{i}"]["cap_hit"] 
                           for i in range(1, contract.years + 1))
        analysis["cap_analysis"] = {
            "total_cap_hit": total_cap_hit,
            "average_cap_hit": total_cap_hit // contract.years if contract.years > 0 else 0,
            "guaranteed_percentage": (contract.guaranteed_money / contract.total_value) * 100 if contract.total_value > 0 else 0
        }
        
        # Dead money analysis
        total_dead_money = sum(analysis["annual_breakdown"][f"year_{i}"]["dead_money"] 
                              for i in range(1, contract.years + 1))
        analysis["dead_money_analysis"] = {
            "total_dead_money": total_dead_money,
            "dead_money_percentage": (total_dead_money / contract.total_value) * 100 if contract.total_value > 0 else 0
        }
        
        return analysis
    
    def get_team_contract_summary(self, team_id: int) -> Dict[str, any]:
        """Get comprehensive contract summary for a team"""
        contracts = self.db.query(Contract).filter(
            Contract.team_id == team_id,
            Contract.is_active == True
        ).all()
        
        if not contracts:
            return {"error": "No active contracts found for team"}
        
        # Calculate totals
        total_contracts = len(contracts)
        total_value = sum(c.total_value for c in contracts)
        total_guaranteed = sum(c.guaranteed_money for c in contracts)
        
        # Contract type breakdown
        contract_types = {}
        for contract in contracts:
            contract_type = contract.contract_type
            if contract_type not in contract_types:
                contract_types[contract_type] = {"count": 0, "total_value": 0}
            contract_types[contract_type]["count"] += 1
            contract_types[contract_type]["total_value"] += contract.total_value
        
        # Position breakdown
        position_contracts = {}
        for contract in contracts:
            player = self.db.query(Player).filter(Player.id == contract.player_id).first()
            if player:
                pos = player.position
                if pos not in position_contracts:
                    position_contracts[pos] = {"count": 0, "total_value": 0}
                position_contracts[pos]["count"] += 1
                position_contracts[pos]["total_value"] += contract.total_value
        
        return {
            "team_id": team_id,
            "total_contracts": total_contracts,
            "total_value": total_value,
            "total_guaranteed": total_guaranteed,
            "guaranteed_percentage": (total_guaranteed / total_value) * 100 if total_value > 0 else 0,
            "contract_types": contract_types,
            "position_breakdown": position_contracts,
            "average_contract_value": total_value // total_contracts if total_contracts > 0 else 0
        }
