"""
Additional API Endpoints for Starforged AI Game Master.
Star Map, Rumor Network, and Audio State management.
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional

# Import systems
from src.starmap import StarMap, Sector
from src.rumor_system import RumorNetwork, RumorType, RumorSource # Fixed import path
from src.hazards import HazardGenerator, Hazard
from src.living_world import WorldSimulator, WorldEvent
import random
import time


# ============================================================================
# Star Map API Endpoints
# ============================================================================

class TravelRequest(BaseModel):
    session_id: str
    system_id: str


def register_starmap_routes(app, SESSIONS):
    """Register star map API routes."""
    
    @app.post("/api/starmap/generate")
    def generate_sector(session_id: str = "default", sector_name: str = "The Forge", system_count: int = 20):
        """Generate a new star sector with faction territories."""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[session_id]
        
        starmap = StarMap()
        starmap.generate_sector(sector_name, system_count)
        
        # Assign Faction Territories
        from src.starmap import Sector
        sector = Sector(sector_name)
        for sid, sys in starmap.systems.items():
            sector.add_system(sys)
            
        # Get factions from state if available
        factions = state.get('world', {}).get('factions', [])
        if not factions:
            # Fallback/Default factions
            factions = [
                {"id": "iron_syndicate", "name": "Iron Syndicate", "influence": 0.7},
                {"id": "keepers", "name": "The Keepers", "influence": 0.5},
                {"id": "archivists", "name": "Archivists", "influence": 0.3}
            ]
            
        starmap.assign_faction_territories(sector, factions)
        
        # Save to state
        state['starmap'] = starmap.to_dict()
        
        return {
            "success": True,
            "sector": sector_name,
            "systems_generated": system_count,
            "factions": factions
        }
    
    @app.post("/api/starmap/travel")
    def travel_to_system(req: TravelRequest):
        """Travel to a star system with hazards and simulation."""
        if req.session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[req.session_id]
        starmap_data = state.get('starmap', {})
        
        if not starmap_data:
            raise HTTPException(status_code=400, detail="No star map generated")
        
        starmap = StarMap.from_dict(starmap_data)
        
        # Find destination
        destination_id = req.system_id
        if destination_id not in starmap.systems:
            raise HTTPException(status_code=404, detail="System not found")
            
        system = starmap.systems[destination_id]
        
        # Check for Hazards
        hazard_gen = HazardGenerator()
        hazard = hazard_gen.generate_travel_hazard(system.star_class.value)
        hazard_data = None
        if hazard:
            hazard_data = hazard.to_dict()
            state.setdefault('hazards', {})['active_hazards'] = [hazard_data]
        else:
            state.setdefault('hazards', {})['active_hazards'] = []
            
        # Run World Simulation
        sim_data = state.get('world_sim', {})
        if not isinstance(sim_data, dict):
            # Convert Pydantic model to dict for legacy simulator
            sim_data = sim_data.dict() if hasattr(sim_data, 'dict') else {}
            
        sim = WorldSimulator.from_dict(sim_data)
        new_events = sim.simulate_turn(state, days_passed=random.randint(1, 4))
        
        # Update state (keep as dict for legacy compatibility if needed, or object)
        # Note: If we assign a dict, world_api.py handles it.
        state['world_sim'] = sim.to_dict()
        
        # Perform Travel
        result = starmap.travel_to(destination_id)
        
        # Update world location
        world = state['world']
        if isinstance(world, dict):
            world['current_location'] = system.name
        else:
            world.current_location = system.name
        
        # Save updated state
        state['starmap'] = starmap.to_dict()
        
        # Integration with Narrator for flavor
        from src.narrator import generate_narrative, NarratorConfig
        hazard_context = f" WARNING: encountered {hazard.name}." if hazard else ""
        
        arrival_text = generate_narrative(
            player_input=f"Travel to {system.name}",
            character_name=state['character'].name if hasattr(state['character'], 'name') else state['character'].get('name', 'Unknown'),
            location=system.name,
            context=f"You arrived at {system.name}.{hazard_context}",
            config=NarratorConfig(backend="gemini")
        )
        
        result.update({
            "hazard": hazard_data,
            "new_world_events": [e.to_dict() for e in new_events],
            "narrative": arrival_text
        })
        
        return result
    
    @app.get("/api/starmap/nearby/{session_id}")
    def get_nearby_systems(session_id: str, count: int = 5):
        """Get nearby star systems for navigation."""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[session_id]
        starmap_data = state.get('starmap', {})
        
        if not starmap_data:
            return {"systems": []}
        
        starmap = StarMap.from_dict(starmap_data)
        return {"systems": starmap.get_nearby_systems(count)}
 
    @app.get("/api/world/events/{session_id}")
    def get_world_events(session_id: str):
        """Get history of world events."""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[session_id]
        sim_state = state.get('world_sim', {})
        
        if isinstance(sim_state, dict):
            events = sim_state.get('events', [])
            counter = sim_state.get('event_counter', 0)
        else:
            events = getattr(sim_state, 'events', [])
            counter = getattr(sim_state, 'event_counter', 0)
            
        return {
            "events": events,
            "event_counter": counter
        }

    @app.get("/api/world/hazards/{session_id}")
    def get_active_hazards(session_id: str):
        """Get active hazards."""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[session_id]
        hazard_state = state.get('hazards', {})
        return {"active_hazards": hazard_state.get('active_hazards', [])}


# ============================================================================
# Rumor Network API Endpoints
# ============================================================================

class GenerateRumorRequest(BaseModel):
    session_id: str
    source: str
    category: Optional[str] = None


class InvestigateRumorRequest(BaseModel):
    session_id: str
    rumor_id: str
    success: bool = True


def register_rumor_routes(app, SESSIONS):
    """Register rumor network API routes."""
    
    @app.post("/api/rumors/generate")
    def generate_rumor(req: GenerateRumorRequest):
        """Generate a new rumor."""
        if req.session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[req.session_id]
        rumors_data = state.get('rumors', {})
        
        network = RumorNetwork.from_dict(rumors_data) if rumors_data else RumorNetwork()
        rumor = network.generate_rumor(req.source, req.category)
        
        # Save updated state
        state['rumors'] = network.to_dict()
        
        return {"success": True, "rumor": rumor.to_dict()}
    
    @app.post("/api/rumors/investigate")
    def investigate_rumor(req: InvestigateRumorRequest):
        """Investigate a rumor."""
        if req.session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[req.session_id]
        rumors_data = state.get('rumors', {})
        
        if not rumors_data:
            raise HTTPException(status_code=400, detail="No rumors exist")
        
        network = RumorNetwork.from_dict(rumors_data)
        result = network.investigate_rumor(req.rumor_id, req.success)
        
        # Save updated state
        state['rumors'] = network.to_dict()
        
        return result
    
    @app.get("/api/rumors/active/{session_id}")
    def get_active_rumors(session_id: str):
        """Get all active rumors."""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[session_id]
        rumors_data = state.get('rumors', {})
        
        if not rumors_data:
            return {"rumors": []}
        
        network = RumorNetwork.from_dict(rumors_data)
        return {"rumors": network.get_active_rumors()}


        return {"rumors": network.get_active_rumors()}
