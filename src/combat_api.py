from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.combat_orchestrator import CombatOrchestrator, EnemyType
from src.game_state import GameState

# Router definition
router = APIRouter(prefix="/api/combat", tags=["combat"])

class CombatStartRequest(BaseModel):
    session_id: str
    enemy_type: str = "SOLDIER" # MINION, SOLDIER, ELITE, BOSS
    count: int = 3
    
class CombatUpdateRequest(BaseModel):
    session_id: str
    player_health: float = 1.0

def register_combat_routes(app, SESSIONS: Dict[str, GameState]):
    """Register combat API routes."""
    
    @app.post("/api/combat/start")
    def start_combat(req: CombatStartRequest):
        """Initialize a new combat encounter."""
        if req.session_id not in SESSIONS:
            if req.session_id == "default":
                 # Auto-init for MVP
                 from src.game_state import CharacterStats, CharacterCondition
                 # We can't easily auto-init full state here, so we rely on server.py having created it.
                 # But usually server.py starts 'default' session on boot or client init.
                 pass
            
            if req.session_id not in SESSIONS:
                 raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[req.session_id]
        
        # Initialize Orchestrator
        orch = CombatOrchestrator()
        
        # Add Enemies
        e_type = getattr(EnemyType, req.enemy_type.upper(), EnemyType.SOLDIER)
        
        for i in range(req.count):
            orch.add_combatant(
                id=f"Hostile-{i+1}",
                name=f"Unit {i+1}",
                enemy_type=e_type,
                threat_level=1.0 if e_type != EnemyType.ELITE else 2.0
            )
            
        # Store in state
        state['combat_orchestrator'] = orch
        state['world'].combat_active = True
        
        return {"success": True, "enemies": req.count}

    @app.get("/api/combat/debug/{session_id}")
    def get_combat_debug(session_id: str):
        """Get debug state for visualizer."""
        if session_id not in SESSIONS:
             raise HTTPException(status_code=404, detail="Session not found")
            
        state = SESSIONS[session_id]
        orch = state.get('combat_orchestrator')
        
        if not orch:
            return {"status": "No active combat system"}
            
        # Update simulation (advance time)
        # In a real game, this happens in game loop. Here we step it on poll.
        # But we need player health. We'll estimate from state or default.
        p_health = state['character'].condition.health / 5.0  if hasattr(state['character'], 'condition') else 1.0
        
        # We perform a tick update to manage tokens
        # We need psyche profile if available
        psyche = state.get('psyche')
        profile = psyche.profile if psyche else None
        
        orch.update(player_health=p_health, profile=profile)
        
        return orch.get_debug_state()

    @app.post("/api/combat/end")
    def end_combat(session_id: str):
        """End current combat."""
        if session_id not in SESSIONS:
             raise HTTPException(status_code=404, detail="Session not found")
             
        state = SESSIONS[session_id]
        state['combat_orchestrator'] = None
        state['world'].combat_active = False
        return {"success": True}

    app.include_router(router)
