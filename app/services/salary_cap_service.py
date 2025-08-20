from sqlalchemy.orm import Session
from typing import Dict, List, Tuple, Optional
from ..database.models import Contract, Team, Player, SalaryCap, TeamSalaryCap
from datetime import datetime, date
import math

class SalaryCapService:
    def __init__(self, db: Session):
        self.db = db
        self.current_year = 2024
        
        # 2024 NFL Salary Cap figures
        self.base_cap = 255400000
        self.minimum_spend = 230000000  # 90% of base cap
        self.rookie_pool = 10000000  # Estimated rookie pool
        
        # Rookie wage scale (2024 figures)
        self.rookie_scale = {
            1: {1: 10000000, 2: 12000000, 3: 14000000, 4: 18000000, 5: 22000000},
            2: {1: 8000000, 2: 9000000, 3: 10000000, 4: 12000000, 5: 14000000},
            3: {1: 6000000, 2: 7000000, 3: 8000000, 4: 9000000, 5: 10000000},
            4: {1: 4000000, 2: 4500000, 3: 5000000, 4: 5500000, 5: 6000000},
            5: {1: 3000000, 2: 3200000, 3: 3400000, 4: 3600000, 5: 3800000},
            6: {1: 2500000, 2: 2600000, 3: 2700000, 4: 2800000, 5: 2900000},
            7: {1: 2000000, 2: 2100000, 3: 2200000, 4: 2300000, 5: 2400000}
        }
    
    def get_current_salary_cap(self) -> Dict[str, int]:
        """Get current year salary cap information"""
        return {
            "year": self.current_year,
            "base_cap": self.base_cap,
            "minimum_spend": self.minimum_spend,
            "rookie_pool": self.rookie_pool
        }
    
    def calculate_contract_cap_hits(self, contract: Contract) -> Dict[str, int]:
        """Calculate annual cap hits for a contract"""
        if not contract.is_active:
            return {}
        
        # Get base salaries for each year
        salaries = [
            contract.year_1_salary,
            contract.year_2_salary,
            contract.year_3_salary,
            contract.year_4_salary,
            contract.year_5_salary
        ]
        
        # Calculate signing bonus proration
        signing_bonus_proration = contract.signing_bonus // contract.years if contract.years > 0 else 0
        
        # Calculate cap hits for each year
        cap_hits = {}
        for i, salary in enumerate(salaries[:contract.years], 1):
            if salary > 0:
                cap_hit = salary + signing_bonus_proration
                cap_hits[f"year_{i}_cap_hit"] = cap_hit
                
                # Update the contract with calculated cap hit
                setattr(contract, f"year_{i}_cap_hit", cap_hit)
        
        return cap_hits
    
    def calculate_team_salary_cap(self, team_id: int, year: int = None) -> Dict[str, any]:
        """Calculate comprehensive salary cap for a team"""
        if year is None:
            year = self.current_year
        
        # Get all active contracts for the team
        contracts = self.db.query(Contract).filter(
            Contract.team_id == team_id,
            Contract.is_active == True
        ).all()
        
        # Calculate cap hits for all contracts
        total_cap_used = 0
        total_dead_money = 0
        contract_details = []
        
        for contract in contracts:
            # Calculate cap hits if not already done
            if not contract.year_1_cap_hit:
                self.calculate_contract_cap_hits(contract)
            
            # Get current year cap hit
            current_year_cap_hit = getattr(contract, f"year_{year - self.current_year + 1}_cap_hit", 0)
            if current_year_cap_hit > 0:
                total_cap_used += current_year_cap_hit
                contract_details.append({
                    "player_id": contract.player_id,
                    "cap_hit": current_year_cap_hit,
                    "base_salary": getattr(contract, f"year_{year - self.current_year + 1}_salary", 0),
                    "contract_type": contract.contract_type
                })
        
        # Calculate dead money
        dead_money = self.calculate_team_dead_money(team_id, year)
        total_dead_money = sum(dead_money.values())
        
        # Top 51 rule: Only top 51 contracts count against cap during offseason
        # For simplicity, we'll use all contracts for now
        top_51_cap_used = total_cap_used
        
        # Calculate cap space
        adjusted_cap = self.base_cap  # Could include carryover and adjustments
        cap_space = adjusted_cap - top_51_cap_used - total_dead_money
        
        return {
            "team_id": team_id,
            "year": year,
            "adjusted_cap": adjusted_cap,
            "total_cap_used": total_cap_used,
            "top_51_cap_used": top_51_cap_used,
            "dead_money": total_dead_money,
            "cap_space": cap_space,
            "cap_percentage": (top_51_cap_used / adjusted_cap) * 100 if adjusted_cap > 0 else 0,
            "contracts": contract_details
        }
    
    def calculate_team_dead_money(self, team_id: int, year: int) -> Dict[str, int]:
        """Calculate dead money for a team in a specific year"""
        contracts = self.db.query(Contract).filter(
            Contract.team_id == team_id,
            Contract.is_active == False  # Inactive contracts may have dead money
        ).all()
        
        dead_money = {}
        for contract in contracts:
            # Get dead money for the specific year
            dead_money_amount = getattr(contract, f"dead_money_year_{year - self.current_year + 1}", 0)
            if dead_money_amount > 0:
                dead_money[f"contract_{contract.id}"] = dead_money_amount
        
        return dead_money
    
    def create_rookie_contract(self, player: Player, team_id: int, draft_round: int, 
                              draft_pick: int, years: int = 4) -> Contract:
        """Create a rookie contract based on draft position"""
        if draft_round > 7:
            draft_round = 7  # Undrafted free agents
        
        # Get base salary from rookie scale
        base_salary = self.rookie_scale[draft_round][1]
        
        # Calculate total value
        total_value = base_salary * years
        
        # Create contract
        contract = Contract(
            player_id=player.id,
            team_id=team_id,
            total_value=total_value,
            guaranteed_money=base_salary,  # First year guaranteed
            years=years,
            year_1_salary=base_salary,
            year_2_salary=base_salary,
            year_3_salary=base_salary,
            year_4_salary=base_salary,
            year_5_salary=base_salary if years > 4 else 0,
            is_rookie_contract=True,
            rookie_scale_year=1,
            contract_type="rookie",
            start_date=datetime.now(),
            end_date=datetime(self.current_year + years, 3, 1),  # March 1st of final year
            is_active=True
        )
        
        # Calculate cap hits
        self.calculate_contract_cap_hits(contract)
        
        return contract
    
    def create_veteran_contract(self, player: Player, team_id: int, 
                               base_salary: int, years: int, 
                               signing_bonus: int = 0, 
                               roster_bonus: int = 0) -> Contract:
        """Create a veteran contract"""
        # Calculate annual salaries (simple escalation)
        annual_salary = base_salary
        total_value = (annual_salary * years) + signing_bonus + roster_bonus
        
        contract = Contract(
            player_id=player.id,
            team_id=team_id,
            total_value=total_value,
            guaranteed_money=signing_bonus,
            years=years,
            year_1_salary=annual_salary,
            year_2_salary=annual_salary + (annual_salary * 0.05),  # 5% increase
            year_3_salary=annual_salary + (annual_salary * 0.10),  # 10% increase
            year_4_salary=annual_salary + (annual_salary * 0.15) if years > 3 else 0,
            year_5_salary=annual_salary + (annual_salary * 0.20) if years > 4 else 0,
            signing_bonus=signing_bonus,
            roster_bonus=roster_bonus,
            contract_type="veteran",
            start_date=datetime.now(),
            end_date=datetime(self.current_year + years, 3, 1),
            is_active=True
        )
        
        # Calculate cap hits
        self.calculate_contract_cap_hits(contract)
        
        return contract
    
    def restructure_contract(self, contract: Contract, 
                           restructure_amount: int) -> Dict[str, any]:
        """Restructure a contract to create cap space"""
        if not contract.is_active:
            return {"error": "Contract is not active"}
        
        # Convert base salary to signing bonus
        current_year = self.current_year
        current_year_salary = getattr(contract, f"year_{1}_salary", 0)
        
        if current_year_salary < restructure_amount:
            return {"error": "Restructure amount exceeds current year salary"}
        
        # Calculate new cap hits
        new_signing_bonus = contract.signing_bonus + restructure_amount
        new_base_salary = current_year_salary - restructure_amount
        
        # Update contract
        contract.signing_bonus = new_signing_bonus
        setattr(contract, "year_1_salary", new_base_salary)
        
        # Recalculate cap hits
        self.calculate_contract_cap_hits(contract)
        
        # Calculate cap savings
        old_cap_hit = current_year_salary + (contract.signing_bonus // contract.years)
        new_cap_hit = new_base_salary + (new_signing_bonus // contract.years)
        cap_savings = old_cap_hit - new_cap_hit
        
        return {
            "success": True,
            "cap_savings": cap_savings,
            "new_cap_hit": new_cap_hit,
            "restructure_amount": restructure_amount
        }
    
    def release_player(self, contract: Contract, 
                      post_june_1: bool = False) -> Dict[str, any]:
        """Release a player and calculate dead money"""
        if not contract.is_active:
            return {"error": "Contract is not active"}
        
        # Calculate dead money
        remaining_signing_bonus = contract.signing_bonus
        years_remaining = contract.years
        
        if post_june_1:
            # Post-June 1 release: dead money hits next year
            dead_money_current = remaining_signing_bonus // years_remaining
            dead_money_next = remaining_signing_bonus - dead_money_current
        else:
            # Pre-June 1 release: all dead money hits immediately
            dead_money_current = remaining_signing_bonus
            dead_money_next = 0
        
        # Update contract
        contract.is_active = False
        contract.dead_money_year_1 = dead_money_current
        contract.dead_money_year_2 = dead_money_next
        
        # Calculate cap savings
        current_year_cap_hit = getattr(contract, f"year_{1}_cap_hit", 0)
        cap_savings = current_year_cap_hit - dead_money_current
        
        return {
            "success": True,
            "cap_savings": cap_savings,
            "dead_money_current": dead_money_current,
            "dead_money_next": dead_money_next,
            "post_june_1": post_june_1
        }
    
    def get_team_cap_summary(self, team_id: int) -> Dict[str, any]:
        """Get comprehensive cap summary for a team"""
        cap_info = self.calculate_team_salary_cap(team_id)
        
        # Get top contracts
        top_contracts = sorted(
            cap_info["contracts"], 
            key=lambda x: x["cap_hit"], 
            reverse=True
        )[:10]
        
        # Get position breakdown
        position_cap = {}
        for contract in cap_info["contracts"]:
            player = self.db.query(Player).filter(Player.id == contract["player_id"]).first()
            if player:
                pos = player.position
                if pos not in position_cap:
                    position_cap[pos] = 0
                position_cap[pos] += contract["cap_hit"]
        
        return {
            **cap_info,
            "top_contracts": top_contracts,
            "position_breakdown": position_cap,
            "cap_efficiency": self.calculate_cap_efficiency(cap_info)
        }
    
    def calculate_cap_efficiency(self, cap_info: Dict[str, any]) -> Dict[str, any]:
        """Calculate cap efficiency metrics"""
        total_cap = cap_info["adjusted_cap"]
        used_cap = cap_info["total_cap_used"]
        
        # Calculate efficiency metrics
        cap_utilization = (used_cap / total_cap) * 100 if total_cap > 0 else 0
        
        # Determine cap health
        if cap_utilization < 80:
            cap_health = "Excellent"
        elif cap_utilization < 90:
            cap_health = "Good"
        elif cap_utilization < 95:
            cap_health = "Fair"
        else:
            cap_health = "Critical"
        
        return {
            "utilization_percentage": round(cap_utilization, 1),
            "health_status": cap_health,
            "flexibility": "High" if cap_utilization < 85 else "Medium" if cap_utilization < 92 else "Low"
        }
