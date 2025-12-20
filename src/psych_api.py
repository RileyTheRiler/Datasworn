from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from src.game_state import GameState

# Router definition
router = APIRouter(prefix="/api/psyche", tags=["psyche"])

def register_psychology_routes(app, SESSIONS: Dict[str, GameState]):
    """Register psychology API routes."""
    
    @app.get("/api/psyche/{session_id}")
    def get_psyche_state(session_id: str):
        """Get the current psychological state."""
        if session_id not in SESSIONS:
            # Fallback for 'default' if it doesn't exist yet (MVP hack)
            if session_id == "default":
                return {"error": "Session not initialized"}
            raise HTTPException(status_code=404, detail="Session not found")
            
        state = SESSIONS[session_id]
        psyche = state['psyche']
        
        # Serialize if pydantic model
        if hasattr(psyche, 'dict'):
            return psyche.dict()
        if hasattr(psyche, 'model_dump'):
            return psyche.model_dump()
            
        return psyche

    @app.get("/api/psyche/default") # Alias for PsycheDashboard default
    def get_default_psyche():
        # Look for default session
        if "default" in SESSIONS:
            return get_psyche_state("default")
        return {} # Empty if not started
