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
        sim = WorldSimulator.from_dict(sim_data)
        new_events = sim.simulate_turn(state, days_passed=random.randint(1, 4))
        state['world_sim'] = sim.to_dict()
        
        # Perform Travel
        result = starmap.travel_to(destination_id)
        
        # Update world location
        state['world'].current_location = system.name
        
        # Save updated state
        state['starmap'] = starmap.to_dict()
        
        # Integration with Narrator for flavor
        from src.narrator import generate_narrative, NarratorConfig
        hazard_context = f" WARNING: encountered {hazard.name}." if hazard else ""
        
        arrival_text = generate_narrative(
            player_input=f"Travel to {system.name}",
            character_name=state['character'].name,
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
        return {
            "events": sim_state.get('events', []),
            "event_counter": sim_state.get('event_counter', 0)
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


# ============================================================================
# Audio State API Endpoints
# ============================================================================

class AudioUpdateRequest(BaseModel):
    session_id: str
    ambient_volume: Optional[float] = None
    music_volume: Optional[float] = None
    voice_volume: Optional[float] = None
    master_volume: Optional[float] = None
    muted: Optional[bool] = None
    current_ambient: Optional[str] = None
    current_music: Optional[str] = None


def register_audio_routes(app, SESSIONS):
    """Register audio state API routes."""
    
    @app.post("/api/audio/update")
    def update_audio_state(req: AudioUpdateRequest):
        """Update audio state."""
        if req.session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[req.session_id]
        audio = state.get('audio', {})
        
        # Update provided fields
        if req.ambient_volume is not None:
            audio['ambient_volume'] = req.ambient_volume
        if req.music_volume is not None:
            audio['music_volume'] = req.music_volume
        if req.voice_volume is not None:
            audio['voice_volume'] = req.voice_volume
        if req.master_volume is not None:
            audio['master_volume'] = req.master_volume
        if req.muted is not None:
            audio['muted'] = req.muted
        if req.current_ambient is not None:
            audio['current_ambient'] = req.current_ambient
        if req.current_music is not None:
            audio['current_music'] = req.current_music
        
        state['audio'] = audio
        
        return {"success": True, "audio": audio}
    
    @app.get("/api/audio/{session_id}")
    def get_audio_state(session_id: str):
        """Get current audio state."""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = SESSIONS[session_id]
        return state.get('audio', {})

    @app.get("/api/audio/state/{session_id}")
    def get_audio_directives(session_id: str):
        """Get audio directives (ambient/music) for AudioManager.jsx."""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
            
        state = SESSIONS[session_id]
        audio = state.get('audio', {})
        
        # Structure as expected by AudioManager.jsx
        return {
            "ambient": {
                "zone_type": audio.get('current_ambient') if isinstance(audio, dict) else audio.current_ambient,
                "tracks": audio.get('current_tracks', []) if isinstance(audio, dict) else audio.current_tracks,
                "volume": audio.get('ambient_volume', 0.5) if isinstance(audio, dict) else audio.ambient_volume
            },
            "music": {
                "track_id": audio.get('current_music') if isinstance(audio, dict) else audio.current_music,
                "filename": audio.get('music_filename') if isinstance(audio, dict) else audio.music_filename,
                "volume": audio.get('music_volume', 0.6) if isinstance(audio, dict) else audio.music_volume
            }
        }
