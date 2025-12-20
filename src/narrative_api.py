from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from src.game_state import GameState

router = APIRouter(prefix="/api/narrative", tags=["narrative"])

def register_narrative_routes(app, sessions: Dict[str, GameState]):
    """Register narrative API routes."""
    
    @app.get("/state")
    async def get_narrative_state(session_id: str = "default"):
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
            
        state = sessions[session_id]
        
        # Access orchestrator data
        orch_state = state.get("narrative_orchestrator")
        if not orch_state:
            return {"error": "No orchestrator state"}
            
        # The data is stored in the 'orchestrator_data' dict
        data = orch_state.orchestrator_data
        
        # 1. Narrative Plants (Promises, Mysteries, etc.)
        narrative_memory = data.get("narrative_memory", {})
        plants = narrative_memory.get("plants", {})
        pending_plants = [
            p for p in plants.values() 
            if p.get("payoff_status") == "pending"
        ]
        
        # Sort by importance
        pending_plants.sort(key=lambda x: x.get("importance", 0), reverse=True)
        
        # 2. Tension
        story_graph = data.get("story_graph", {})
        tension_curve = story_graph.get("tension_curve", [])
        current_tension = tension_curve[-1] if tension_curve else 0.0
        
        # 3. Themes
        theme_engine = data.get("theme_engine", {})
        active_themes = theme_engine.get("active_themes", [])
        
        return {
            "tension": current_tension,
            "active_subplots": [p["description"] for p in pending_plants], # simplified list
            "plants": pending_plants, # full data for UI
            "themes": active_themes,
            "scene_count": narrative_memory.get("current_scene", 0)
        }

    app.include_router(router)
