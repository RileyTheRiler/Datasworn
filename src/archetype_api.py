"""
API endpoints for the archetype system.

Provides endpoints for:
- Submitting behavior observations
- Retrieving archetype profiles
- Getting psychological/moral needs
- Checking revelation progress
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.narrative.archetype_types import (
    ArchetypeProfile,
    BehaviorInstance,
    NeedState,
    RevelationProgress,
)
from src.observation.archetype_observer import ArchetypeObserver
from src.inference.archetype_inference import ArchetypeInferenceEngine


# Request/Response Models
class ObserveBehaviorRequest(BaseModel):
    """Request to observe a player behavior."""
    session_id: str
    behavior_type: str  # "dialogue", "action", "interrogation", "crisis"
    description: str
    context: str
    scene_id: str
    npc_involved: Optional[str] = None
    target: Optional[str] = None


class ArchetypeProfileResponse(BaseModel):
    """Response containing archetype profile."""
    primary: str
    secondary: str
    tertiary: str
    confidence: float
    archetypes: Dict[str, float]
    overcontrolled_tendency: float
    undercontrolled_tendency: float
    observation_count: int
    last_updated: Optional[str]


class NeedStateResponse(BaseModel):
    """Response containing psychological and moral needs."""
    psychological_wound: str
    psychological_need: str
    psychological_awareness: float
    moral_corruption: str
    moral_need: str
    moral_awareness: float
    wound_to_corruption_chain: str
    psychological_evidence_count: int
    moral_evidence_count: int


class RevelationProgressResponse(BaseModel):
    """Response containing revelation progress."""
    current_stage: str
    progress_percentage: float
    mirror_moment_delivered: bool
    cost_revealed: bool
    origin_glimpsed: bool
    choice_crystallized: bool
    murder_solution_delivered: bool
    mirror_speech_given: bool
    moral_decision_made: bool
    moral_decision_choice: Optional[str]
    path_determined: Optional[str]


def register_archetype_routes(app, sessions: Dict[str, Any]):
    """Register archetype API routes with the FastAPI app."""
    
    router = APIRouter(prefix="/api/archetype", tags=["archetype"])
    
    # Initialize observer and engine
    observer = ArchetypeObserver()
    engine = ArchetypeInferenceEngine()
    
    @router.post("/observe")
    async def observe_behavior(req: ObserveBehaviorRequest):
        """
        Submit a behavior observation.
        
        This endpoint records player behavior and updates their archetype profile.
        """
        if req.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[req.session_id]
        
        # Create observation based on behavior type
        if req.behavior_type == "dialogue":
            observation = observer.observe_dialogue(
                player_choice=req.description,
                context=req.context,
                scene_id=req.scene_id,
                npc_involved=req.npc_involved,
            )
        elif req.behavior_type == "action":
            observation = observer.observe_action(
                action_description=req.description,
                context=req.context,
                scene_id=req.scene_id,
                target=req.target,
            )
        elif req.behavior_type == "interrogation":
            observation = observer.observe_interrogation(
                approach=req.description,
                npc=req.npc_involved or "Unknown",
                context=req.context,
                scene_id=req.scene_id,
            )
        elif req.behavior_type == "crisis":
            observation = observer.observe_crisis_response(
                crisis_description=req.context,
                response=req.description,
                context=req.context,
                scene_id=req.scene_id,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid behavior_type: {req.behavior_type}"
            )
        
        
        # Get or create archetype profile
        # State['psyche'] is a Pydantic model, need to check if attribute exists
        psyche = state['psyche']
        if not hasattr(psyche, 'archetype_profile') or psyche.archetype_profile is None:
            # Create new profile as a plain Python object (not Pydantic)
            psyche.archetype_profile = ArchetypeProfile()
        
        profile = psyche.archetype_profile
        
        # Update profile with new observation
        old_profile = profile
        new_profile = engine.update_profile(profile, [observation])
        psyche.archetype_profile = new_profile
        
        # Detect shifts
        shift = engine.detect_shift(old_profile, new_profile, observation)
        
        # Store observation in behavior history
        if not hasattr(psyche, 'behavior_history') or psyche.behavior_history is None:
            psyche.behavior_history = []
        psyche.behavior_history.append(observation)
        
        return {
            "observation_recorded": True,
            "signals_detected": observation.archetype_signals,
            "primary_archetype": new_profile.primary_archetype,
            "confidence": new_profile.confidence,
            "shift_detected": shift is not None,
            "shift": shift.to_dict() if shift else None,
        }
    
    @router.get("/profile")
    async def get_archetype_profile(session_id: str):
        """Get the current archetype profile."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[session_id]
        
        # Get or create profile
        psyche = state['psyche']
        if not hasattr(psyche, 'archetype_profile') or psyche.archetype_profile is None:
            psyche.archetype_profile = ArchetypeProfile()
        
        profile = psyche.archetype_profile
        
        return ArchetypeProfileResponse(
            primary=profile.primary_archetype,
            secondary=profile.secondary_archetype,
            tertiary=profile.tertiary_archetype,
            confidence=profile.confidence,
            archetypes=profile._get_archetype_weights(),
            overcontrolled_tendency=profile.overcontrolled_tendency,
            undercontrolled_tendency=profile.undercontrolled_tendency,
            observation_count=profile.observation_count,
            last_updated=profile.last_updated.isoformat() if profile.last_updated else None,
        )
    
    @router.get("/needs")
    async def get_needs(session_id: str):
        """Get the current psychological and moral needs."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[session_id]
        
        # Get profile and behavior history
        psyche = state['psyche']
        if not hasattr(psyche, 'archetype_profile') or psyche.archetype_profile is None:
            psyche.archetype_profile = ArchetypeProfile()
        
        profile = psyche.archetype_profile
        behavior_history = getattr(psyche, 'behavior_history', [])
        
        # Infer needs
        needs = engine.infer_needs(profile, behavior_history)
        
        return NeedStateResponse(
            psychological_wound=needs.psychological_wound,
            psychological_need=needs.psychological_need,
            psychological_awareness=needs.psychological_awareness,
            moral_corruption=needs.moral_corruption,
            moral_need=needs.moral_need,
            moral_awareness=needs.moral_awareness,
            wound_to_corruption_chain=needs.wound_to_corruption_chain,
            psychological_evidence_count=len(needs.psychological_evidence),
            moral_evidence_count=len(needs.moral_evidence),
        )
    
    @router.get("/revelation")
    async def get_revelation_progress(session_id: str):
        """Get the current revelation progress."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[session_id]
        
        # Get or create revelation progress
        psyche = state['psyche']
        if not hasattr(psyche, 'revelation_progress') or psyche.revelation_progress is None:
            psyche.revelation_progress = RevelationProgress()
        
        progress = psyche.revelation_progress
        
        return RevelationProgressResponse(
            current_stage=progress.current_stage,
            progress_percentage=progress.progress_percentage,
            mirror_moment_delivered=progress.mirror_moment_delivered,
            cost_revealed=progress.cost_revealed,
            origin_glimpsed=progress.origin_glimpsed,
            choice_crystallized=progress.choice_crystallized,
            murder_solution_delivered=progress.murder_solution_delivered,
            mirror_speech_given=progress.mirror_speech_given,
            moral_decision_made=progress.moral_decision_made,
            moral_decision_choice=progress.moral_decision_choice,
            path_determined=progress.path_determined,
        )
    
    @router.post("/test-inference")
    async def test_inference(
        session_id: str,
        dialogue_samples: List[str],
    ):
        """
        Test endpoint for inference engine.
        
        Simulates multiple dialogue observations and returns the resulting profile.
        Useful for verification and testing.
        """
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create test observations
        observations = []
        for i, dialogue in enumerate(dialogue_samples):
            obs = observer.observe_dialogue(
                player_choice=dialogue,
                context="Test scenario",
                scene_id=f"test_scene_{i}",
            )
            observations.append(obs)
        
        # Create test profile
        profile = ArchetypeProfile()
        profile = engine.update_profile(profile, observations)
        
        # Infer needs
        needs = engine.infer_needs(profile, observations)
        
        return {
            "profile": {
                "primary": profile.primary_archetype,
                "secondary": profile.secondary_archetype,
                "confidence": profile.confidence,
                "weights": profile._get_archetype_weights(),
            },
            "needs": {
                "psychological_wound": needs.psychological_wound,
                "psychological_need": needs.psychological_need,
                "moral_corruption": needs.moral_corruption,
                "moral_need": needs.moral_need,
            },
            "observations_processed": len(observations),
        }
    
    # Register router with app
    app.include_router(router)
