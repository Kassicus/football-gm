from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database.connection import get_db
from ..services.salary_cap_service import SalaryCapService
from ..services.contract_service import ContractService

router = APIRouter()

@router.get("/overview")
def get_salary_cap_overview(db: Session = Depends(get_db)):
    """Get overall salary cap information"""
    salary_service = SalaryCapService(db)
    
    return {
        "current_salary_cap": salary_service.get_current_salary_cap(),
        "cap_year": "2024"
    }

@router.get("/team/{team_id}")
def get_team_salary_cap(team_id: int, db: Session = Depends(get_db)):
    """Get salary cap information for a specific team"""
    salary_service = SalaryCapService(db)
    
    try:
        cap_info = salary_service.calculate_team_salary_cap(team_id)
        return cap_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating salary cap: {str(e)}")

@router.get("/team/{team_id}/summary")
def get_team_cap_summary(team_id: int, db: Session = Depends(get_db)):
    """Get comprehensive cap summary for a team"""
    salary_service = SalaryCapService(db)
    
    try:
        summary = salary_service.get_team_cap_summary(team_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cap summary: {str(e)}")

@router.get("/team/{team_id}/contracts")
def get_team_contracts(team_id: int, db: Session = Depends(get_db)):
    """Get all contracts for a team"""
    contract_service = ContractService(db)
    
    try:
        summary = contract_service.get_team_contract_summary(team_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving contracts: {str(e)}")

@router.get("/contract/{contract_id}")
def get_contract_analysis(contract_id: int, db: Session = Depends(get_db)):
    """Get detailed analysis of a specific contract"""
    contract_service = ContractService(db)
    
    try:
        analysis = contract_service.get_contract_analysis(contract_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing contract: {str(e)}")

@router.post("/contract/{contract_id}/restructure")
def restructure_contract(
    contract_id: int, 
    restructure_amount: int = Query(..., description="Amount to restructure in dollars"),
    db: Session = Depends(get_db)
):
    """Restructure a contract to create cap space"""
    contract_service = ContractService(db)
    
    try:
        result = contract_service.restructure_contract(contract_id, restructure_amount)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restructuring contract: {str(e)}")

@router.post("/contract/{contract_id}/release")
def release_player(
    contract_id: int,
    post_june_1: bool = Query(False, description="Whether to use post-June 1 designation"),
    db: Session = Depends(get_db)
):
    """Release a player and calculate dead money"""
    contract_service = ContractService(db)
    
    try:
        result = contract_service.release_player(contract_id, post_june_1)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error releasing player: {str(e)}")

@router.post("/player/{player_id}/franchise-tag")
def franchise_tag_player(
    player_id: int,
    team_id: int = Query(..., description="Team ID to apply franchise tag"),
    db: Session = Depends(get_db)
):
    """Apply franchise tag to a player"""
    contract_service = ContractService(db)
    
    try:
        result = contract_service.franchise_tag_player(player_id, team_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying franchise tag: {str(e)}")

@router.post("/player/{player_id}/extend")
def extend_player_contract(
    player_id: int,
    team_id: int = Query(..., description="Team ID for the extension"),
    base_salary: int = Query(..., description="Base salary per year"),
    years: int = Query(..., description="Contract length in years"),
    signing_bonus: int = Query(0, description="Signing bonus amount"),
    db: Session = Depends(get_db)
):
    """Negotiate a contract extension with a player"""
    contract_service = ContractService(db)
    
    try:
        result = contract_service.negotiate_contract_extension(
            player_id, team_id, base_salary, years, signing_bonus
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error negotiating extension: {str(e)}")

@router.get("/player/{player_id}/contract")
def get_player_contract(player_id: int, db: Session = Depends(get_db)):
    """Get current contract for a player"""
    contract_service = ContractService(db)
    
    try:
        contract = contract_service.get_player_contract(player_id)
        if not contract:
            return {"message": "Player has no active contract"}
        
        # Get contract analysis
        analysis = contract_service.get_contract_analysis(contract.id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving player contract: {str(e)}")

@router.get("/player/{player_id}/contract-history")
def get_player_contract_history(player_id: int, db: Session = Depends(get_db)):
    """Get contract history for a player"""
    contract_service = ContractService(db)
    
    try:
        contracts = contract_service.get_player_contract_history(player_id)
        return [
            {
                "contract_id": contract.id,
                "team_id": contract.team_id,
                "total_value": contract.total_value,
                "years": contract.years,
                "contract_type": contract.contract_type,
                "start_date": contract.start_date,
                "end_date": contract.end_date,
                "is_active": contract.is_active
            }
            for contract in contracts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving contract history: {str(e)}")

@router.get("/league/overview")
def get_league_cap_overview(db: Session = Depends(get_db)):
    """Get league-wide salary cap overview"""
    salary_service = SalaryCapService(db)
    
    try:
        # Get cap info for all teams
        from ..database.models import Team
        teams = db.query(Team).all()
        
        league_overview = {
            "total_teams": len(teams),
            "salary_cap": salary_service.get_current_salary_cap(),
            "teams": []
        }
        
        for team in teams:
            try:
                cap_info = salary_service.calculate_team_salary_cap(team.id)
                league_overview["teams"].append({
                    "team_id": team.id,
                    "team_name": f"{team.city} {team.name}",
                    "cap_used": cap_info["total_cap_used"],
                    "cap_space": cap_info["cap_space"],
                    "cap_percentage": cap_info["cap_percentage"]
                })
            except Exception as e:
                # Skip teams with errors
                continue
        
        return league_overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting league overview: {str(e)}")
