"""
NPC Scheduling API Endpoints

Provides REST API for NPC schedules, dialogue, and world memory.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.ai import Scheduler, NavigationManager
from src.ai.npc_state import NPCMemoryState, MemoryTokenType, get_default_duration
from src.dialogue import DialogueSelector, DialogueContext
from src.world import WorldMemoryManager, EventType


# Global instances (will be initialized in server.py)
scheduler: Optional[Scheduler] = None
navigation: Optional[NavigationManager] = None
dialogue_selector: Optional[DialogueSelector] = None
world_memory: Optional[WorldMemoryManager] = None


# Request/Response Models
class AssignScheduleRequest(BaseModel):
    npc_id: str
    archetype: str
    region: str = "default"


class InterruptScheduleRequest(BaseModel):
    npc_id: str
    reason: str
    priority: int
    behavior: str
    location: Optional[str] = None
    duration: int = 0
    resume_after: bool = True


class GetDialogueRequest(BaseModel):
    npc_id: str
    interaction_type: str = "greeting"
    context: Dict[str, Any] = {}


class RecordEventRequest(BaseModel):
    area_id: str
    event_type: str
    description: str
    actor: Optional[str] = None
    witnesses: Optional[List[str]] = None
    severity: float = 0.5


def register_npc_scheduling_routes(app, sessions: Dict):
    """Register all NPC scheduling and dialogue routes"""
    
    global scheduler, navigation, dialogue_selector, world_memory
    
    # Initialize systems
    scheduler = Scheduler()
    navigation = NavigationManager()
    dialogue_selector = DialogueSelector()
    world_memory = WorldMemoryManager()
    
    # ========================================================================
    # SCHEDULE ENDPOINTS
    # ========================================================================
    
    @app.get("/api/npc/schedule/{npc_id}")
    def get_npc_schedule(npc_id: str):
        """Get current schedule for an NPC"""
        if not scheduler:
            raise HTTPException(status_code=500, detail="Scheduler not initialized")
        
        schedule = scheduler.get_schedule(npc_id)
        if not schedule:
            raise HTTPException(status_code=404, detail=f"No schedule found for {npc_id}")
        
        return schedule.to_dict()
    
    @app.get("/api/npc/schedules/active")
    def get_active_schedules():
        """Get all active schedules"""
        if not scheduler:
            raise HTTPException(status_code=500, detail="Scheduler not initialized")
        
        schedules = scheduler.get_all_active_schedules()
        return {
            "count": len(schedules),
            "schedules": {npc_id: sched.to_dict() for npc_id, sched in schedules.items()}
        }
    
    @app.post("/api/npc/schedule/assign")
    def assign_schedule(req: AssignScheduleRequest):
        """Assign a schedule to an NPC"""
        if not scheduler:
            raise HTTPException(status_code=500, detail="Scheduler not initialized")
        
        schedule = scheduler.assign_schedule(
            npc_id=req.npc_id,
            archetype=req.archetype,
            region=req.region
        )
        
        if not schedule:
            raise HTTPException(status_code=400, detail=f"Failed to assign schedule for archetype '{req.archetype}'")
        
        return {
            "success": True,
            "npc_id": req.npc_id,
            "archetype": req.archetype,
            "schedule": schedule.to_dict()
        }
    
    @app.post("/api/npc/schedule/interrupt")
    def interrupt_schedule(req: InterruptScheduleRequest):
        """Interrupt an NPC's current schedule"""
        if not scheduler:
            raise HTTPException(status_code=500, detail="Scheduler not initialized")
        
        success = scheduler.interrupt(
            npc_id=req.npc_id,
            reason=req.reason,
            priority=req.priority,
            behavior=req.behavior,
            location=req.location,
            duration=req.duration,
            resume_after=req.resume_after
        )
        
        return {
            "success": success,
            "npc_id": req.npc_id,
            "reason": req.reason
        }
    
    @app.post("/api/npc/schedule/resume/{npc_id}")
    def resume_schedule(npc_id: str):
        """Resume an NPC's paused schedule"""
        if not scheduler:
            raise HTTPException(status_code=500, detail="Scheduler not initialized")
        
        success = scheduler.resume(npc_id)
        return {
            "success": success,
            "npc_id": npc_id
        }
    
    # ========================================================================
    # DIALOGUE ENDPOINTS
    # ========================================================================
    
    @app.post("/api/dialogue/select")
    def select_dialogue(req: GetDialogueRequest):
        """Get contextual dialogue for an NPC"""
        if not dialogue_selector:
            raise HTTPException(status_code=500, detail="Dialogue selector not initialized")
        
        # Build context from request
        context = DialogueContext(**req.context)
        
        # Select dialogue
        line = dialogue_selector.select_dialogue(
            npc_id=req.npc_id,
            interaction_type=req.interaction_type,
            context=context
        )
        
        if not line:
            return {
                "success": False,
                "message": "No matching dialogue found"
            }
        
        return {
            "success": True,
            "text": line.text,
            "animation": line.animation,
            "sound_effect": line.sound_effect,
            "triggers": line.triggers,
            "behavior": line.behavior,
            "reputation_change": line.reputation_change,
            "relationship_change": line.relationship_change,
        }
    
    @app.get("/api/dialogue/{npc_id}/greeting")
    def get_greeting(npc_id: str, session_id: str = "default"):
        """Get a greeting dialogue for an NPC"""
        if not dialogue_selector:
            raise HTTPException(status_code=500, detail="Dialogue selector not initialized")
        
        # Build context from session state
        context = DialogueContext()
        if session_id in sessions:
            state = sessions[session_id]
            # Extract context from game state
            context.player_honor = state.get('psyche', {}).get('profile', {}).get('identity', {}).get('honor', 0.5)
        
        line = dialogue_selector.get_greeting(npc_id, context)
        
        if not line:
            return {"text": "Greetings, traveler."}
        
        return {
            "text": line.text,
            "animation": line.animation,
        }
    
    # ========================================================================
    # WORLD MEMORY ENDPOINTS
    # ========================================================================
    
    @app.get("/api/world/memory/{area_id}")
    def get_area_memory(area_id: str, limit: int = 5):
        """Get rumors and recent events for an area"""
        if not world_memory:
            raise HTTPException(status_code=500, detail="World memory not initialized")
        
        rumors = world_memory.get_rumors(area_id, limit=limit)
        events = world_memory.get_events(area_id, max_age_minutes=360)  # Last 6 hours
        
        return {
            "area_id": area_id,
            "rumors": rumors,
            "recent_events": [event.to_dict() for event in events],
        }
    
    @app.post("/api/world/memory/event")
    def record_world_event(req: RecordEventRequest):
        """Record a witnessed event in world memory"""
        if not world_memory:
            raise HTTPException(status_code=500, detail="World memory not initialized")
        
        try:
            event_type = EventType(req.event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {req.event_type}")
        
        event = world_memory.record_event(
            area_id=req.area_id,
            event_type=event_type,
            description=req.description,
            actor=req.actor,
            witnesses=req.witnesses,
            severity=req.severity
        )
        
        return {
            "success": True,
            "event": event.to_dict()
        }
    
    @app.get("/api/world/memory/status")
    def get_world_memory_status():
        """Get status of world memory system"""
        if not world_memory:
            raise HTTPException(status_code=500, detail="World memory not initialized")
        
        return world_memory.get_status()
    
    # ========================================================================
    # NAVIGATION ENDPOINTS
    # ========================================================================
    
    @app.get("/api/navigation/status")
    def get_navigation_status():
        """Get status of navigation system"""
        if not navigation:
            raise HTTPException(status_code=500, detail="Navigation not initialized")
        
        return navigation.get_status()
