from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel

from src.narrative.factions import FactionManager, FactionStanding

router = APIRouter(prefix="/api/factions", tags=["factions"])

class FactionStatus(BaseModel):
    id: str
    name: str
    type: str
    reputation: float
    standing: str
    trade_modifier: float
    description: str

class ReputationRequest(BaseModel):
    session_id: str
    reputation_change: float
    reason: str = "Debug action"

def register_faction_routes(app, sessions):
    manager = FactionManager()

    @router.get("/status/{session_id}")
    def get_faction_status(session_id: str) -> Dict[str, List[FactionStatus]]:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[session_id]
        character_rep = state['character'].reputation
        
        results = []
        for faction in manager.get_all_factions():
            current_rep = character_rep.get(faction.id, faction.default_reputation)
            standing = manager.get_standing(faction.id, current_rep)
            
            results.append(FactionStatus(
                id=faction.id,
                name=faction.name,
                type=faction.type,
                reputation=current_rep,
                standing=standing.name,
                trade_modifier=manager.get_trade_modifier(current_rep),
                description=faction.description
            ))
            
        return {"factions": results}

    @router.get("/{faction_id}/{session_id}")
    def get_faction_details(faction_id: str, session_id: str) -> FactionStatus:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
            
        faction = manager.get_faction(faction_id)
        if not faction:
            raise HTTPException(status_code=404, detail="Faction not found")
            
        state = sessions[session_id]
        current_rep = state['character'].reputation.get(faction_id, faction.default_reputation)
        standing = manager.get_standing(faction.id, current_rep)
        
        return FactionStatus(
            id=faction.id,
            name=faction.name,
            type=faction.type,
            reputation=current_rep,
            standing=standing.name,
            trade_modifier=manager.get_trade_modifier(current_rep),
            description=faction.description
        )

    @router.post("/{faction_id}/reputation")
    def modify_reputation(faction_id: str, req: ReputationRequest):
        """Debug endpoint to modify reputation."""
        if req.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
            
        faction = manager.get_faction(faction_id)
        if not faction:
            raise HTTPException(status_code=404, detail="Faction not found")
            
        state = sessions[req.session_id]
        current_rep = state['character'].reputation.get(faction_id, faction.default_reputation)
        
        # Apply change
        new_rep = max(-100.0, min(100.0, current_rep + req.reputation_change))
        state['character'].reputation[faction_id] = new_rep
        
        standing = manager.get_standing(faction_id, new_rep)
        
        # Dispatch event
        try:
            from src.world_api import add_manual_event
            change_str = "increased" if req.reputation_change >= 0 else "decreased"
            add_manual_event(
                req.session_id,
                "faction_update", 
                {
                    "description": f"Reputation with {faction.name} {change_str} to {new_rep:.1f} ({standing.name}). Reason: {req.reason}",
                    "location": "System-wide",
                    "importance": 1
                }
            )
        except Exception as e:
            print(f"Failed to dispatch faction event: {e}")

        return {
            "faction_id": faction_id,
            "old_reputation": current_rep,
            "new_reputation": new_rep,
            "new_standing": standing.name,
            "reason": req.reason
        }

    app.include_router(router)
