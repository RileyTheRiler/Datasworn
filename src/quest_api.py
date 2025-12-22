"""
Quest System API Endpoints

Provides REST API for quest management and world state tracking.
"""

from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

from src.quests.graph import QuestGraph
from src.quests.state import QuestState
from src.quests.world_state import WorldState as QuestWorldState


# Request/Response Models
class QuestProgressRequest(BaseModel):
    session_id: str
    objective_id: Optional[str] = None
    complete: bool = False
    fail: bool = False
    alternate: bool = False


class WorldStateFlagRequest(BaseModel):
    session_id: str
    scope: str
    key: str
    value: Any

class POIDiscoverRequest(BaseModel):
    session_id: str = "default"
    x: float
    y: float


def register_quest_routes(app, sessions: Dict):
    """Register quest-related API routes."""
    
    def _get_quest_graph(session_id: str) -> QuestGraph:
        """Get or create quest graph for session."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[session_id]
        
        # Initialize quest graph if not present
        if 'quest_graph' not in state:
            graph = QuestGraph()
            # Load quest definitions from data directory
            try:
                graph.load_phases_from_yaml("data/story/quest_phases.yaml")
                graph.load_quests_from_yaml("data/story/quests")
            except Exception as e:
                print(f"Warning: Could not load quest data: {e}")
            
            state['quest_graph'] = graph
        
        return state['quest_graph']
    
    def _get_world_state(session_id: str) -> QuestWorldState:
        """Get or create world state for session."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[session_id]
        
        # Initialize world state if not present
        if 'quest_world_state' not in state:
            state['quest_world_state'] = QuestWorldState()
        
        return state['quest_world_state']
    
    @app.get("/api/quests/list")
    def list_quests(session_id: str = "default", phase: Optional[int] = None):
        """
        Get all quests with their current states.
        
        Query params:
        - session_id: Game session ID
        - phase: Optional phase filter
        """
        graph = _get_quest_graph(session_id)
        
        # Get quests by state
        available = graph.get_available_quests(phase)
        active = graph.get_active_quests()
        
        return {
            "available": [q.to_dict() for q in available],
            "active": [q.to_dict() for q in active],
            "current_phase": graph.state_manager.current_phase,
            "current_scene": graph.state_manager.current_scene
        }
    
    @app.get("/api/quests/{quest_id}")
    def get_quest(quest_id: str, session_id: str = "default"):
        """Get detailed information about a specific quest."""
        graph = _get_quest_graph(session_id)
        
        if quest_id not in graph.nodes:
            raise HTTPException(status_code=404, detail="Quest not found")
        
        node = graph.nodes[quest_id]
        state_entry = graph.state_manager.states.get(quest_id)
        
        # Check prerequisites
        prereqs_met, unmet = graph.check_prerequisites(quest_id)
        
        return {
            "quest": node.to_dict(),
            "state": state_entry.to_dict() if state_entry else None,
            "prerequisites_met": prereqs_met,
            "unmet_prerequisites": unmet
        }
    
    @app.post("/api/quests/{quest_id}/start")
    def start_quest(quest_id: str, session_id: str = "default"):
        """Start a quest."""
        graph = _get_quest_graph(session_id)
        
        success, message = graph.start_quest(quest_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message}
    
    @app.post("/api/quests/{quest_id}/complete")
    def complete_quest(quest_id: str, session_id: str = "default", 
                      alternate: bool = False, alternate_path: str = ""):
        """Complete a quest."""
        graph = _get_quest_graph(session_id)
        
        success, message = graph.complete_quest(quest_id, alternate, alternate_path)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message}
    
    @app.post("/api/quests/{quest_id}/fail")
    def fail_quest(quest_id: str, session_id: str = "default", reason: str = ""):
        """Fail a quest."""
        graph = _get_quest_graph(session_id)
        
        success = graph.state_manager.fail_quest(quest_id, reason)
        
        if not success:
            raise HTTPException(status_code=400, detail="Could not fail quest")
        
        return {"success": True, "message": f"Quest '{quest_id}' failed"}
    
    @app.get("/api/quests/convergence/{node_id}")
    def get_convergence_status(node_id: str, session_id: str = "default"):
        """Get status of a convergence node."""
        graph = _get_quest_graph(session_id)
        
        status = graph.get_convergence_status(node_id)
        return status
    
    @app.get("/api/quests/phase/{phase_id}/status")
    def get_phase_status(phase_id: int, session_id: str = "default"):
        """Get critical path status for a phase."""
        graph = _get_quest_graph(session_id)
        
        status = graph.get_critical_path_status(phase_id)
        return status
    
    @app.post("/api/quests/phase/advance")
    def advance_phase(new_phase: int, session_id: str = "default"):
        """Advance to a new phase."""
        graph = _get_quest_graph(session_id)
        
        graph.advance_phase(new_phase)
        
        return {
            "success": True,
            "new_phase": new_phase,
            "message": f"Advanced to phase {new_phase}"
        }
    
    # World State Endpoints
    @app.get("/api/world-state")
    def get_world_state(session_id: str = "default"):
        """Get current world state snapshot."""
        world_state = _get_world_state(session_id)
        
        return {
            "flags": world_state.get_flags(),
            "metadata": world_state.metadata
        }
    
    @app.post("/api/world-state/flags")
    def set_world_flag(request: WorldStateFlagRequest):
        """Set a world state flag."""
        world_state = _get_world_state(request.session_id)
        
        # For simple flags, just set them
        if isinstance(request.value, bool) and request.value:
            flag_key = f"{request.scope}.{request.key}"
            world_state.set_flag(flag_key)
        elif isinstance(request.value, bool) and not request.value:
            flag_key = f"{request.scope}.{request.key}"
            world_state.unset_flag(flag_key)
        else:
            # For complex values, use metadata
            world_state.set_metadata(f"{request.scope}.{request.key}", request.value)
        
        return {"success": True}
    
    @app.get("/api/world-state/flags/{scope}/{key}")
    def get_world_flag(scope: str, key: str, session_id: str = "default"):
        """Get a specific world state flag or metadata value."""
        world_state = _get_world_state(session_id)
        
        flag_key = f"{scope}.{key}"
        
        # Check if it's a boolean flag
        if world_state.has_flag(flag_key):
            return {"value": True, "type": "flag"}
        
        # Check metadata
        metadata_value = world_state.get_metadata(flag_key)
        if metadata_value is not None:
            return {"value": metadata_value, "type": "metadata"}
        
        return {"value": None, "type": "none"}

    # POI System Endpoints
    def _get_poi_heatmap(session_id: str):
        """Get or create POI heatmap for session."""
        from src.quests.poi_system import POIHeatmap
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[session_id]
        
        # Initialize POI heatmap if not present
        if 'poi_heatmap' not in state:
            heatmap = POIHeatmap()
            # Load POIs from data directory
            try:
                heatmap.load_from_json("data/world/points_of_interest.json")
            except Exception as e:
                print(f"Warning: Could not load POI data: {e}")
            
            state['poi_heatmap'] = heatmap
        
        return state['poi_heatmap']
    
    @app.get("/api/poi/nearby")
    def get_nearby_pois(session_id: str = "default", x: float = 0.0, y: float = 0.0, 
                        radius: Optional[float] = None, biome: Optional[str] = None,
                        poi_type: Optional[str] = None):
        """
        Get POIs near a location.
        """
        heatmap = _get_poi_heatmap(session_id)
        
        location = (x, y)
        nearby = heatmap.get_nearby_pois(location, radius, biome=biome, poi_type=poi_type)
        
        return {
            "pois": [poi.to_dict() for poi in nearby],
            "count": len(nearby)
        }
    
    @app.post("/api/poi/discover")
    def discover_pois(request: POIDiscoverRequest):
        """Discover POIs at current location."""
        heatmap = _get_poi_heatmap(request.session_id)
        
        location = (request.x, request.y)
        heatmap.player_location = location
        newly_discovered = heatmap.discover_pois(location)
        
        return {
            "discovered": [poi.to_dict() for poi in newly_discovered],
            "count": len(newly_discovered)
        }
    
    @app.get("/api/poi/quest-hooks")
    def get_quest_hooks(session_id: str = "default", x: float = 0.0, y: float = 0.0,
                        radius: Optional[float] = None):
        """Get quest IDs that can be started from nearby POIs."""
        heatmap = _get_poi_heatmap(session_id)
        
        location = (x, y)
        quest_hooks = heatmap.get_quest_hooks_nearby(location, radius)
        
        return {
            "quest_hooks": quest_hooks,
            "count": len(quest_hooks)
        }

    @app.get("/api/poi/summary")
    def get_poi_summary(session_id: str = "default"):
        """Get summary of POI distribution."""
        heatmap = _get_poi_heatmap(session_id)
        
        return heatmap.get_heatmap_summary()
