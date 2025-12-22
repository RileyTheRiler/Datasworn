"""
World Simulation API
Endpoints for controlling and querying the world simulation.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

from src.world.simulation.simulation_loop import SimulationLoop
from src.world.simulation.config_loader import get_config_loader
from src.world.simulation.weather import WeatherState
from src.game_state import GameState

# Global store for active simulations
# Key: session_id, Value: SimulationLoop
ACTIVE_SIMULATIONS: Dict[str, SimulationLoop] = {}

def get_simulation(session_id: str, sessions: Dict[str, GameState]) -> SimulationLoop:
    """Get active simulation for session, restoring from state if needed."""
    if session_id in ACTIVE_SIMULATIONS:
        return ACTIVE_SIMULATIONS[session_id]
    
    # Try to restore from GameState
    if session_id in sessions:
        state = sessions[session_id]
        # Access WorldSimState object
        world_sim = state.get('world_sim')
        serialized = None
        
        if world_sim:
            if isinstance(world_sim, dict):
                serialized = world_sim.get('serialized_state')
            else:
                serialized = getattr(world_sim, 'serialized_state', None)
                
        if serialized:
            try:
                print(f"Restoring simulation for session {session_id}...")
                sim = SimulationLoop.from_dict(serialized)
                ACTIVE_SIMULATIONS[session_id] = sim
                return sim
            except Exception as e:
                print(f"Failed to restore simulation: {e}")
        
        # Initialize new if not found
        print(f"Initializing new simulation for session {session_id}...")
        sim = SimulationLoop()
        # Default to core region for now, should come from game state location
        current_region = "core_nexus"
        sim.initialize_from_region(current_region)
        ACTIVE_SIMULATIONS[session_id] = sim
        return sim
    
    raise HTTPException(status_code=404, detail="Session not found")

class WorldStatus(BaseModel):
    weather: str
    weather_modifiers: Dict[str, float]
    traffic_congestion: float
    law_suspicion: Dict[str, float]
    active_vignettes: List[Dict[str, Any]]
    time_of_day: str

class TickRequest(BaseModel):
    session_id: str
    hours: float = 1.0

class WeatherRequest(BaseModel):
    session_id: str
    weather_state: str
    sector: Optional[str] = None

class VignetteResponse(BaseModel):
    id: str
    description: str
    outcomes: Dict[str, str]
    timestamp: float

def add_manual_event(session_id: str, event_type: str, data: Dict[str, Any]):
    """Manually inject an event into the simulation."""
    if session_id in ACTIVE_SIMULATIONS:
        sim = ACTIVE_SIMULATIONS[session_id]
        from src.world.simulation.event_dispatcher import EventType
        try:
            # Map string to EventType if possible
            e_type = None
            for et in EventType:
                if et.value == event_type:
                    e_type = et
                    break
            
            if not e_type:
                # Fallback to general type if faction_update not found (though it should be now)
                e_type = EventType.FACTION_UPDATE
                
            sim.dispatcher.publish(e_type, data)
        except Exception as e:
            print(f"Failed to dispatch manual event: {e}")

def register_world_routes(app: FastAPI, sessions: Dict[str, GameState]):
    """Register world simulation routes."""
    
    @app.get("/api/world/status/{session_id}")
    async def get_world_status(session_id: str):
        """Get current status of the simulated world."""
        sim = get_simulation(session_id, sessions)
        state = sessions.get(session_id)
        if not state:
            raise HTTPException(status_code=404, detail="Session not found")
            
        world = state['world']
        current_sector = getattr(world, 'current_location', 'unknown_sector') if not isinstance(world, dict) else world.get('current_location', 'unknown_sector')
        
        # Hydrate weather
        weather_cond = sim.weather.get_weather(current_sector)
        weather_str = weather_cond.state.value if weather_cond else "unknown"
        modifiers = weather_cond.modifiers if weather_cond else {}
        
        # Hydrate traffic
        congestion = sim.traffic.get_congestion(current_sector)
        
        return {
            "weather": weather_str,
            "modifiers": modifiers,
            "congestion": congestion,
            "suspicion": sim.law.player_suspicion,
        }

    @app.post("/api/world/tick")
    async def tick_world(req: TickRequest):
        """Advance world simulation."""
        sim = get_simulation(req.session_id, sessions)
        state = sessions.get(req.session_id)
        
        # Convert GameState model to dict for tick
        events = sim.tick(state) 
        
        # Persist back to GameState
        if 'world_sim' in state:
             world_sim = state['world_sim']
             # Update serialized state
             if isinstance(world_sim, dict):
                 world_sim['serialized_state'] = sim.to_dict()
                 # Append events
                 if 'events' not in world_sim:
                     world_sim['events'] = []
                 for evt in events:
                     world_sim['events'].append(evt)
             else:
                 # It's a Pydantic model
                 world_sim.serialized_state = sim.to_dict()
                 for evt in events:
                     world_sim.events.append(evt)
        
        return {
            "events": events,
            "tick_count": len(events)
        }
    
    @app.get("/api/world/simulation/events/{session_id}")
    async def get_recent_events(session_id: str, limit: int = 20):
        """Get log of recent world events."""
        sim = get_simulation(session_id, sessions)
        events = sim.dispatcher.get_recent_events(limit)
        return [
            {
                "type": e.event_type.value,
                "data": e.data,
                "timestamp": e.timestamp,
                "id": e.event_id
            }
            for e in events
        ]
    
    @app.post("/api/world/debug/weather")
    async def set_world_weather(req: WeatherRequest):
        """Debug: Force set weather."""
        sim = get_simulation(req.session_id, sessions)
        state = sessions.get(req.session_id)
        
        world = state['world']
        current_sector = getattr(world, 'current_location', 'unknown_sector') if not isinstance(world, dict) else world.get('current_location', 'unknown_sector')
        sector = req.sector or current_sector
        
        try:
            w_state = WeatherState(req.weather_state)
            sim.weather.set_weather(sector, w_state)
            return {"status": "success", "weather": w_state.value}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid weather state")

    @app.get("/api/world/heatmaps/{session_id}")
    async def get_heatmaps(session_id: str):
        """Get data for debug visualization."""
        sim = get_simulation(session_id, sessions)
        return {
            "suspicion": sim.law.player_suspicion,
            "congestion": sim.traffic.congestion_map,
            "wildlife": sim.wildlife.biome_densities
        }
