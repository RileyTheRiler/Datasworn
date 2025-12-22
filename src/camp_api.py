"""
Camp System API Routes.

Provides REST endpoints for the living hub/camp system.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from src.narrative.camp_layout import get_camp_layout_dict, get_zone
from src.narrative.camp_routines import (
    get_routine, get_all_routines, get_current_activities as get_routines_activities,
    get_npcs_at_location, get_npcs_available_for_dialogue, Weather, Season
)
from src.narrative.camp_dialogue import get_camp_dialogue, CampDialogueContext
from src.narrative.hub_interactions import HubInteractionManager
from src.narrative.camp_arcs import CampArcManager, ArcStep
from src.narrative.camp_events import CampEventManager
from src.narrative.camp_journal import CampJournal


# Request models
class InteractRequest(BaseModel):
    npc_id: str
    player_location: str


class AdvanceArcRequest(BaseModel):
    flag: Optional[str] = None


class StartEventRequest(BaseModel):
    event_id: str


class AffordanceRequest(BaseModel):
    affordance_type: str  # sit, chore, gift, drink, gamble
    npc_id: Optional[str] = None
    spot_id: Optional[str] = None


def register_camp_routes(app: FastAPI, sessions: Dict[str, Any]):
    """Register camp system API routes."""
    
    # Initialize managers (in production, these would be per-session)
    interaction_managers: Dict[str, HubInteractionManager] = {}
    arc_managers: Dict[str, CampArcManager] = {}
    event_managers: Dict[str, CampEventManager] = {}
    journals: Dict[str, CampJournal] = {}
    
    def get_or_create_managers(session_id: str):
        """Get or create managers for a session."""
        if session_id not in interaction_managers:
            interaction_managers[session_id] = HubInteractionManager()
        if session_id not in arc_managers:
            arc_managers[session_id] = CampArcManager()
        if session_id not in event_managers:
            event_managers[session_id] = CampEventManager()
        if session_id not in journals:
            journals[session_id] = CampJournal()
        
        return (
            interaction_managers[session_id],
            arc_managers[session_id],
            event_managers[session_id],
            journals[session_id]
        )
    
    @app.get("/api/camp/layout")
    async def get_camp_layout():
        """Get complete camp zone structure."""
        return {"layout": get_camp_layout_dict()}
    
    @app.get("/api/camp/routines")
    async def get_camp_routines(
        session_id: str = "default",
        hour: int = 12,
        weather: str = "clear",
        season: str = "summer"
    ):
        """Get current activities for all NPCs at given hour."""
        try:
            weather_enum = Weather(weather.lower())
        except ValueError:
            weather_enum = Weather.CLEAR
        
        try:
            season_enum = Season(season.lower())
        except ValueError:
            season_enum = Season.SUMMER
        
        activities = get_routines_activities(hour, weather_enum, season_enum)
        
        return {
            "hour": hour,
            "weather": weather,
            "season": season,
            "activities": {
                npc_id: {
                    "activity": act.activity,
                    "location": act.location,
                    "intent": act.intent.value,
                    "interruptible": act.interruptible,
                    "dialogue_available": act.dialogue_available,
                }
                for npc_id, act in activities.items()
            }
        }
    
    @app.post("/api/camp/interact")
    async def initiate_camp_interaction(
        req: InteractRequest,
        session_id: str = "default"
    ):
        """Trigger proximity interaction if conditions met."""
        try:
            if session_id not in sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            interaction_mgr, arc_mgr, _, _ = get_or_create_managers(session_id)
            
            # Get NPC locations from routines
            state = sessions[session_id]
            world = state.get('world')
            if isinstance(world, dict):
                hour = world.get('current_hour', 12)
            else:
                hour = getattr(world, 'current_hour', 12)
            
            
            activities = get_routines_activities(hour)
            npc_locations = {npc_id: act.location for npc_id, act in activities.items()}
            
            # Check proximity
            triggered = interaction_mgr.check_proximity(
                req.player_location,
                npc_locations,
                hour
            )
            
            if not triggered:
                return {"triggered": False, "message": "No interaction available"}
            
            # Start walk-and-talk
            sequence = interaction_mgr.initiate_walk_and_talk(req.npc_id)
            dialogue = sequence.get_current_dialogue()
            
            # Record interaction in arc system
            arc_mgr.record_interaction(req.npc_id, f"Walk-and-talk at {req.player_location}")
            
            return {
                "triggered": True,
                "npc_id": req.npc_id,
                "sequence_id": sequence.sequence_id,
                "dialogue": dialogue,
                "current_leg": sequence.current_leg.value
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Interaction Error: {str(e)}")
    
    @app.post("/api/camp/interact/{npc_id}/advance")
    async def advance_interaction(npc_id: str, session_id: str = "default"):
        """Advance an active interaction sequence."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        interaction_mgr, _, _, _ = get_or_create_managers(session_id)
        
        dialogue = interaction_mgr.advance_sequence(npc_id)
        
        if dialogue is None:
            return {"completed": True, "dialogue": None}
        
        return {"completed": False, "dialogue": dialogue}
    
    @app.post("/api/camp/interact/{npc_id}/abort")
    async def abort_interaction(npc_id: str, session_id: str = "default"):
        """Gracefully abort an interaction."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        interaction_mgr, _, _, _ = get_or_create_managers(session_id)
        
        abort_dialogue = interaction_mgr.abort_interaction(npc_id)
        
        return {"aborted": True, "dialogue": abort_dialogue}
    
    @app.get("/api/camp/arcs/morale")
    async def get_morale_status(session_id: str = "default"):
        """Get morale status for all NPCs and crew."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        _, arc_mgr, _, _ = get_or_create_managers(session_id)
        
        return arc_mgr.get_morale_status()

    @app.get("/api/camp/arcs/{npc_id}")
    async def get_npc_arc_state(npc_id: str, session_id: str = "default"):
        """Get arc state for specific NPC."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        _, arc_mgr, _, _ = get_or_create_managers(session_id)
        
        state = arc_mgr.get_arc_state(npc_id)
        if not state:
            raise HTTPException(status_code=404, detail=f"NPC not found: {npc_id}")
        
        return state.to_dict()
    
    @app.post("/api/camp/arcs/{npc_id}/advance")
    async def advance_npc_arc(
        npc_id: str,
        req: AdvanceArcRequest,
        session_id: str = "default"
    ):
        """Advance arc or set flag."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        _, arc_mgr, _, journal = get_or_create_managers(session_id)
        
        if req.flag:
            # Set flag
            success = arc_mgr.set_flag(npc_id, req.flag)
            if not success:
                raise HTTPException(status_code=404, detail=f"NPC not found: {npc_id}")
            
            # Log to journal
            journal.log_moment(
                f"{npc_id.title()}: Flag set - {req.flag}",
                characters_involved=[npc_id],
                emotional_tone="narrative"
            )
            
            return {"flag_set": req.flag, "npc_id": npc_id}
        else:
            # Advance arc
            advanced = arc_mgr.advance_arc(npc_id)
            state = arc_mgr.get_arc_state(npc_id)
            
            if advanced and state:
                # Log to journal
                journal.log_moment(
                    f"{npc_id.title()}'s story progresses to {state.current_step.value}",
                    characters_involved=[npc_id],
                    emotional_tone="narrative",
                    morale_impact=0.05
                )
            
            return {
                "advanced": advanced,
                "current_step": state.current_step.value if state else None
            }
    

    
    @app.get("/api/camp/events/check")
    async def check_camp_events(session_id: str = "default", hour: int = 12):
        """Check for triggered events based on world state."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        _, arc_mgr, event_mgr, _ = get_or_create_managers(session_id)
        
        # Get available NPCs
        available_npcs = get_npcs_available_for_dialogue(hour)
        
        # Check triggers
        event = event_mgr.check_triggers(
            crew_morale=arc_mgr.crew_morale,
            hour=hour,
            available_npcs=available_npcs
        )
        
        if event:
            return {
                "event_available": True,
                "event": event.to_dict()
            }
        
        return {"event_available": False}
    
    @app.post("/api/camp/events/{event_id}/start")
    async def start_camp_event(event_id: str, session_id: str = "default"):
        """Initiate a camp event."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        _, _, event_mgr, journal = get_or_create_managers(session_id)
        
        dialogue_part = event_mgr.start_event(event_id)
        
        if not dialogue_part:
            raise HTTPException(status_code=404, detail=f"Event not found: {event_id}")
        
        # Log to journal
        event = event_mgr.active_event
        if event:
            journal.log_moment(
                f"Camp event: {event.name}",
                characters_involved=event.participants,
                emotional_tone="social",
                morale_impact=event.morale_effect
            )
        
        return {
            "event_id": event_id,
            "speaker": dialogue_part.speaker,
            "text": dialogue_part.text,
            "reactions": dialogue_part.reactions
        }
    
    @app.post("/api/camp/events/advance")
    async def advance_camp_event(session_id: str = "default"):
        """Advance to next part of active event."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        _, _, event_mgr, _ = get_or_create_managers(session_id)
        
        dialogue_part = event_mgr.advance_event()
        
        if not dialogue_part:
            # Event complete
            morale_effect = event_mgr.get_event_morale_effect()
            return {
                "completed": True,
                "morale_effect": morale_effect
            }
        
        return {
            "completed": False,
            "speaker": dialogue_part.speaker,
            "text": dialogue_part.text,
            "reactions": dialogue_part.reactions
        }
    
    @app.get("/api/camp/journal")
    async def get_camp_journal(session_id: str = "default", limit: int = 10):
        """Get recent journal entries."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        _, _, _, journal = get_or_create_managers(session_id)
        
        return {
            "entries": journal.get_summary(limit=limit),
            "visual_state": journal.visual_state.to_dict()
        }
    
    @app.get("/api/camp/journal/narrative")
    async def get_journal_narrative(session_id: str = "default", days: int = 7):
        """Get narrative summary of recent camp events."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        _, _, _, journal = get_or_create_managers(session_id)
        
        return {"narrative": journal.generate_narrative_summary(days=days)}
    
    @app.post("/api/camp/affordance")
    async def perform_camp_affordance(
        req: AffordanceRequest,
        session_id: str = "default"
    ):
        """Handle player affordance actions."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        _, arc_mgr, _, journal = get_or_create_managers(session_id)
        
        # Get dialogue response
        context_map = {
            "sit": CampDialogueContext.SITTING_TOGETHER,
            "chore": CampDialogueContext.CHORE_HELP,
            "gift": CampDialogueContext.GIFT_ACCEPT,
            "drink": CampDialogueContext.DRINKING,
            "gamble": CampDialogueContext.GAMBLING,
        }
        
        context = context_map.get(req.affordance_type, CampDialogueContext.GREETING)
        
        dialogue = None
        morale_delta = 0.0
        
        if req.npc_id:
            # Get NPC arc state for trust level
            arc_state = arc_mgr.get_arc_state(req.npc_id)
            trust_level = arc_state.relationship_level if arc_state else 0.5
            
            dialogue = get_camp_dialogue(req.npc_id, context, trust_level=trust_level)
            
            # Apply morale/trust effects
            if req.affordance_type in ["gift", "chore"]:
                morale_delta = 0.05
                arc_mgr.modify_morale(req.npc_id, delta=0.05, affect_crew=True)
            elif req.affordance_type in ["drink", "gamble"]:
                morale_delta = 0.03
                arc_mgr.modify_morale(req.npc_id, delta=0.03, affect_crew=True)
            elif req.affordance_type == "sit":
                morale_delta = 0.02
                arc_mgr.modify_morale(req.npc_id, delta=0.02)
            
            # Log to journal
            journal.log_moment(
                f"{req.affordance_type.title()} with {req.npc_id.title()}",
                characters_involved=[req.npc_id] if req.npc_id else [],
                emotional_tone="social",
                morale_impact=morale_delta
            )
        
        return {
            "affordance_type": req.affordance_type,
            "npc_id": req.npc_id,
            "dialogue": dialogue,
            "morale_delta": morale_delta
        }
