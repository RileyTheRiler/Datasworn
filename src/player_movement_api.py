"""
Player Movement API

Handles player position tracking and movement within the game world.
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Tuple
import math


class MoveRequest(BaseModel):
    session_id: str = "default"
    x: float
    y: float
    validate_distance: bool = True  # Optional: prevent teleporting


class LocationResponse(BaseModel):
    x: float
    y: float
    nearby_pois: int = 0


def register_player_movement_routes(app, sessions: Dict):
    """Register player movement API routes."""
    
    MAX_MOVE_DISTANCE = 200.0  # Maximum distance player can move in one action
    
    def _get_player_location(session_id: str) -> Tuple[float, float]:
        """Get current player location from session."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[session_id]
        if 'world' not in state or not hasattr(state['world'], 'player_location'):
            # Default location if not set
            return (100.0, 100.0)
        
        return state['world'].player_location
    
    def _set_player_location(session_id: str, x: float, y: float):
        """Update player location in session."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[session_id]
        state['world'].player_location = (x, y)
    
    def _calculate_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)
    
    @app.post("/api/player/move")
    def move_player(request: MoveRequest):
        """
        Move player to a new location.
        
        Optionally validates that the move distance is reasonable
        to prevent teleporting across the map.
        """
        current_location = _get_player_location(request.session_id)
        new_location = (request.x, request.y)
        
        # Validate move distance if requested
        if request.validate_distance:
            distance = _calculate_distance(current_location, new_location)
            if distance > MAX_MOVE_DISTANCE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Move distance ({distance:.1f}) exceeds maximum ({MAX_MOVE_DISTANCE})"
                )
        
        # Update location
        _set_player_location(request.session_id, request.x, request.y)
        
        # Get nearby POIs count for response
        from src.quests.poi_system import POIHeatmap
        poi_count = 0
        try:
            if 'poi_heatmap' in sessions[request.session_id]:
                heatmap = sessions[request.session_id]['poi_heatmap']
                nearby = heatmap.get_nearby_pois(new_location, radius=100)
                poi_count = len(nearby)
        except Exception:
            pass
        
        return {
            "success": True,
            "location": {"x": request.x, "y": request.y},
            "previous_location": {"x": current_location[0], "y": current_location[1]},
            "distance_moved": _calculate_distance(current_location, new_location),
            "nearby_pois": poi_count
        }
    
    @app.get("/api/player/location")
    def get_player_location(session_id: str = "default"):
        """Get current player location."""
        location = _get_player_location(session_id)
        
        # Get nearby POIs count
        poi_count = 0
        try:
            if 'poi_heatmap' in sessions[session_id]:
                heatmap = sessions[session_id]['poi_heatmap']
                nearby = heatmap.get_nearby_pois(location, radius=100)
                poi_count = len(nearby)
        except Exception:
            pass
        
        return {
            "x": location[0],
            "y": location[1],
            "nearby_pois": poi_count
        }
    
    @app.post("/api/player/teleport")
    def teleport_player(request: MoveRequest):
        """
        Teleport player to any location (debug/admin command).
        Bypasses distance validation.
        """
        request.validate_distance = False
        return move_player(request)
