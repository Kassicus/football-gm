from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
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

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Contract Terms
    total_value = Column(Integer)  # Total contract value in dollars
    guaranteed_money = Column(Integer, default=0)
    years = Column(Integer, nullable=False)
    
    # Annual Breakdown (Base Salary)
    year_1_salary = Column(Integer, default=0)
    year_2_salary = Column(Integer, default=0)
    year_3_salary = Column(Integer, default=0)
    year_4_salary = Column(Integer, default=0)
    year_5_salary = Column(Integer, default=0)
    
    # Annual Breakdown (Cap Hit)
    year_1_cap_hit = Column(Integer, default=0)
    year_2_cap_hit = Column(Integer, default=0)
    year_3_cap_hit = Column(Integer, default=0)
    year_4_cap_hit = Column(Integer, default=0)
    year_5_cap_hit = Column(Integer, default=0)
    
    # Bonuses
    signing_bonus = Column(Integer, default=0)
    roster_bonus = Column(Integer, default=0)
    workout_bonus = Column(Integer, default=0)
    performance_bonus = Column(Integer, default=0)
    
    # Rookie Contract Specific
    is_rookie_contract = Column(Boolean, default=False)
    rookie_scale_year = Column(Integer)  # Year of rookie scale (1-5)
    
    # Contract Status
    contract_type = Column(String(20))  # rookie, veteran, extension, franchise_tag, transition_tag
    is_active = Column(Boolean, default=True)
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Dead Money Tracking
    dead_money_year_1 = Column(Integer, default=0)
    dead_money_year_2 = Column(Integer, default=0)
    dead_money_year_3 = Column(Integer, default=0)
    dead_money_year_4 = Column(Integer, default=0)
    dead_money_year_5 = Column(Integer, default=0)

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

class SalaryCap(Base):
    __tablename__ = "salary_caps"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, unique=True)
    base_cap = Column(Integer, nullable=False)  # Base salary cap
    adjusted_cap = Column(Integer, nullable=False)  # After adjustments
    
    # Cap adjustments
    carryover_amount = Column(Integer, default=0)
    adjustment_amount = Column(Integer, default=0)
    
    # Rookie pool allocation
    rookie_pool = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class TeamSalaryCap(Base):
    __tablename__ = "team_salary_caps"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Cap space
    adjusted_cap = Column(Integer, nullable=False)
    total_cap_used = Column(Integer, nullable=False)
    cap_space = Column(Integer, nullable=False)
    
    # Dead money
    total_dead_money = Column(Integer, default=0)
    
    # Roster counts
    top_51_count = Column(Integer, default=0)  # Top 51 contracts count against cap
    total_contracts = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
