import json
import os
from sqlalchemy.orm import Session
from .connection import SessionLocal, create_tables
from .models import Team, Player, Position, Contract
from datetime import datetime

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
        teams_file = os.path.join('data', 'teams.json')
        if os.path.exists(teams_file):
            with open(teams_file, 'r') as f:
                teams_data = json.load(f)
            
            for team_data in teams_data:
                team = Team(**team_data)
                db.add(team)
            print(f"Added {len(teams_data)} teams")
        else:
            print("teams.json not found, skipping team initialization")
        
        # Load and insert positions
        positions_file = os.path.join('data', 'positions.json')
        if os.path.exists(positions_file):
            with open(positions_file, 'r') as f:
                positions_data = json.load(f)
            
            for pos_data in positions_data:
                position = Position(**pos_data)
                db.add(position)
            print(f"Added {len(positions_data)} positions")
        else:
            print("positions.json not found, skipping position initialization")
        
        # Load and insert sample players
        players_file = os.path.join('data', 'players.json')
        if os.path.exists(players_file):
            with open(players_file, 'r') as f:
                players_data = json.load(f)
            
            for player_data in players_data:
                player = Player(**player_data)
                db.add(player)
            print(f"Added {len(players_data)} sample players")
        else:
            print("players.json not found, skipping player initialization")
        
        # Commit to get player IDs
        db.commit()
        
        # Load and insert sample contracts
        contracts_file = os.path.join('data', 'contracts.json')
        if os.path.exists(contracts_file):
            with open(contracts_file, 'r') as f:
                contracts_data = json.load(f)
            
            for contract_data in contracts_data:
                # Convert date strings to datetime objects
                if 'start_date' in contract_data:
                    contract_data['start_date'] = datetime.fromisoformat(contract_data['start_date'].replace('Z', '+00:00'))
                if 'end_date' in contract_data:
                    contract_data['end_date'] = datetime.fromisoformat(contract_data['end_date'].replace('Z', '+00:00'))
                
                contract = Contract(**contract_data)
                db.add(contract)
            print(f"Added {len(contracts_data)} sample contracts")
        else:
            print("contracts.json not found, skipping contract initialization")
        
        db.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
