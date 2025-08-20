from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
from ..database.models import Player, Position
import math

class PlayerEvaluationService:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_overall_rating(self, player: Player) -> int:
        """Calculate overall rating based on position-specific attributes"""
        position = self.db.query(Position).filter(Position.code == player.position).first()
        if not position:
            return 50  # Default rating if position not found
        
        # Get key attributes for this position
        key_attrs = [
            getattr(position, 'key_attribute_1', 'overall_rating'),
            getattr(position, 'key_attribute_2', 'overall_rating'),
            getattr(position, 'key_attribute_3', 'overall_rating')
        ]
        
        # Calculate weighted average based on position
        total_weight = 0
        weighted_sum = 0
        
        for i, attr in enumerate(key_attrs):
            if hasattr(player, attr):
                weight = 0.5 if i == 0 else 0.3 if i == 1 else 0.2
                value = getattr(player, attr)
                weighted_sum += value * weight
                total_weight += weight
        
        # Add physical attributes (universal)
        physical_weight = 0.2
        physical_avg = (player.speed + player.strength + player.agility) / 3
        weighted_sum += physical_avg * physical_weight
        total_weight += physical_weight
        
        # Add mental attributes (universal)
        mental_weight = 0.15
        mental_avg = (player.football_iq + player.leadership + player.work_ethic) / 3
        weighted_sum += mental_avg * mental_weight
        total_weight += mental_weight
        
        overall = int(weighted_sum / total_weight)
        return max(1, min(99, overall))  # Clamp between 1-99
    
    def calculate_potential(self, player: Player) -> int:
        """Calculate potential rating based on age, work ethic, and current ratings"""
        base_potential = player.overall_rating
        
        # Age factor (younger players have higher potential)
        age_factor = max(0.8, 1.2 - (player.age - 21) * 0.02)
        
        # Work ethic factor
        work_ethic_factor = 0.8 + (player.work_ethic / 100) * 0.4
        
        # Years pro factor (less experience = higher potential)
        experience_factor = max(0.7, 1.3 - (player.years_pro * 0.05))
        
        potential = int(base_potential * age_factor * work_ethic_factor * experience_factor)
        return max(1, min(99, potential))
    
    def get_position_grade(self, player: Player) -> str:
        """Get letter grade for player based on overall rating"""
        if player.overall_rating >= 90:
            return "A+"
        elif player.overall_rating >= 85:
            return "A"
        elif player.overall_rating >= 80:
            return "A-"
        elif player.overall_rating >= 75:
            return "B+"
        elif player.overall_rating >= 70:
            return "B"
        elif player.overall_rating >= 65:
            return "B-"
        elif player.overall_rating >= 60:
            return "C+"
        elif player.overall_rating >= 55:
            return "C"
        elif player.overall_rating >= 50:
            return "C-"
        else:
            return "D"
    
    def get_development_trajectory(self, player: Player) -> str:
        """Determine if player is improving, declining, or stable"""
        if player.age <= 23:
            return "Rising Star"
        elif player.age <= 26:
            return "Peak Performance"
        elif player.age <= 29:
            return "Prime Years"
        elif player.age <= 32:
            return "Veteran Leader"
        elif player.age <= 35:
            return "Declining"
        else:
            return "End of Career"
    
    def get_injury_risk(self, player: Player) -> str:
        """Assess injury risk based on age and injury history"""
        if player.injury_prone:
            return "High Risk"
        
        age_risk = max(0, (player.age - 25) * 0.1)
        if age_risk < 0.2:
            return "Low Risk"
        elif age_risk < 0.4:
            return "Moderate Risk"
        else:
            return "High Risk"
    
    def get_trade_value(self, player: Player) -> Dict[str, any]:
        """Calculate trade value for a player"""
        base_value = player.overall_rating * 1000000  # $1M per overall point
        
        # Age adjustment
        if player.age <= 25:
            age_multiplier = 1.5
        elif player.age <= 28:
            age_multiplier = 1.2
        elif player.age <= 31:
            age_multiplier = 1.0
        elif player.age <= 34:
            age_multiplier = 0.7
        else:
            age_multiplier = 0.4
        
        # Contract adjustment (simplified)
        contract_multiplier = 0.8 if player.years_pro > 8 else 1.0
        
        # Position value adjustment
        position_values = {
            'QB': 1.5, 'DE': 1.3, 'WR': 1.2, 'CB': 1.1,
            'LT': 1.2, 'TE': 1.0, 'RB': 0.9, 'ILB': 0.9
        }
        position_multiplier = position_values.get(player.position, 1.0)
        
        trade_value = int(base_value * age_multiplier * contract_multiplier * position_multiplier)
        
        return {
            "estimated_value": trade_value,
            "age_multiplier": age_multiplier,
            "position_multiplier": position_multiplier,
            "contract_multiplier": contract_multiplier
        }
    
    def get_comparison_data(self, player: Player, position: str = None) -> Dict[str, any]:
        """Get comparison data for a player against others at their position"""
        if not position:
            position = player.position
        
        # Get all players at this position
        position_players = self.db.query(Player).filter(
            Player.position == position,
            Player.roster_status == "active"
        ).all()
        
        if not position_players:
            return {}
        
        # Calculate statistics
        ratings = [p.overall_rating for p in position_players]
        avg_rating = sum(ratings) / len(ratings)
        
        # Find percentile
        ratings.sort()
        player_index = ratings.index(player.overall_rating)
        percentile = (player_index / len(ratings)) * 100
        
        return {
            "position": position,
            "total_players": len(position_players),
            "average_rating": round(avg_rating, 1),
            "player_percentile": round(percentile, 1),
            "rank": len([r for r in ratings if r > player.overall_rating]) + 1
        }
