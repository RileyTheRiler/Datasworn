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

    @router.get("/character/{name}")
    async def get_character_profile(name: str):
        from src.narrative.secondary_characters import get_character_data
        data = get_character_data(name)
        if not data:
            raise HTTPException(status_code=404, detail=f"Character {name} not found")
        return data

    @router.post("/character/{name}/reveal")
    async def trigger_character_revelation(name: str, session_id: str = "default"):
        """Debug endpoint to force check/trigger revelations."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
            
        from src.narrative.secondary_characters import check_micro_revelation, get_character_data
        
        # In a real scenario, we'd pull context from the state
        # For this debug endpoint, we'll try to trigger all of them by simulating high trust
        # and checking what comes back
        
        # This is a bit of a hack for the 'reveal' endpoint without a specific context body
        # It just returns what *would* be revealed if the conditions were met (or what is already revealed)
        
        data = get_character_data(name)
        if not data:
            raise HTTPException(status_code=404, detail=f"Character {name} not found")
            
        # Return the revelation text for inspection
        return {
            "revelations": data["micro_revelations"]
        }

    @router.get("/ship")
    async def get_ship_identity():
        from src.narrative.exile_gambit import get_ship_data
        return get_ship_data()

    @router.get("/ship/zones")
    async def get_ship_zones():
        from src.narrative.exile_gambit import get_all_zones
        return get_all_zones()

    @router.get("/ship/zone/{zone_id}")
    async def get_zone_details(zone_id: str, archetype: str = None):
        from src.narrative.exile_gambit import get_zone_details
        data = get_zone_details(zone_id, player_archetype=archetype)
        if not data:
            raise HTTPException(status_code=404, detail=f"Zone {zone_id} not found")
        return data

    @router.post("/check-revelation")
    async def check_revelation(request: Dict[str, Any], session_id: str = "default"):
        """
        Check if a revelation should trigger for an NPC given the current context.
        
        Request body:
        {
            "npc_id": "torres",
            "context": {
                "topic": "military service",
                "trust_score": 0.8,
                "player_archetype": "CONTROLLER"
            }
        }
        """
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        from src.narrative.revelation_manager import RevelationManager
        
        npc_id = request.get("npc_id")
        context = request.get("context", {})
        
        if not npc_id:
            raise HTTPException(status_code=400, detail="npc_id required")
        
        # Get or create revelation manager from state
        state = sessions[session_id]
        rev_state = state.get("narrative", {}).get("revelation_manager", {})
        
        if rev_state:
            manager = RevelationManager.from_dict(rev_state)
        else:
            manager = RevelationManager()
        
        # Check for revelation
        revelation = manager.check_for_revelations(npc_id, context)
        
        if revelation:
            return {
                "should_trigger": True,
                "revelation": {
                    "id": revelation.id,
                    "text": revelation.revelation_text,
                    "trigger": revelation.trigger_condition
                }
            }
        else:
            return {
                "should_trigger": False,
                "revelation": None
            }

    @router.get("/dialogue/{npc_name}")
    async def get_npc_dialogue(npc_name: str, session_id: str = "default", context: str = "casual"):
        """
        Get archetype-specific dialogue for an NPC based on player's psychological profile.
        
        Args:
            npc_name: NPC identifier (torres, kai, okonkwo, vasquez, ember)
            session_id: Game session ID
            context: Dialogue context (first_meeting, casual, murder_question, archetype_specific)
        
        Returns:
            Dialogue line appropriate for the player's archetype and relationship state
        """
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        from src.narrative.dialogue_banks import get_dialogue, get_relationship_stage, DialogueContext, RelationshipStage
        from src.relationship_system import RelationshipWeb
        
        state = sessions[session_id]
        
        # Get player's dominant archetype
        try:
            dominant_wound = state['psyche'].profile.identity.wound_profile.dominant_wound
            archetype = dominant_wound.value if hasattr(dominant_wound, 'value') else str(dominant_wound)
        except Exception as e:
            print(f"Warning: Could not get player archetype: {e}")
            archetype = "unknown"
        
        # Get relationship data
        relationships_data = state.get('relationships', {})
        if hasattr(relationships_data, 'model_dump'):
            relationships = RelationshipWeb.from_dict(relationships_data.model_dump())
        elif isinstance(relationships_data, dict):
            relationships = RelationshipWeb.from_dict(relationships_data)
        else:
            relationships = relationships_data
        
        # Get NPC from relationship web
        npc_id = npc_name.lower()
        if npc_id not in relationships.crew:
            raise HTTPException(status_code=404, detail=f"NPC not found: {npc_name}")
        
        npc = relationships.crew[npc_id]
        
        # Get trust score and interaction count
        if isinstance(npc, dict):
            trust_score = npc.get('trust', 0.5)
            interaction_count = npc.get('interaction_count', 0)
        else:
            trust_score = npc.trust
            interaction_count = getattr(npc, 'interaction_count', 0)
        
        # Determine relationship stage
        relationship_stage = get_relationship_stage(interaction_count)
        
        # Map context string to enum
        try:
            dialogue_context = DialogueContext(context)
        except ValueError:
            dialogue_context = DialogueContext.CASUAL
        
        # Get dialogue
        dialogue = get_dialogue(
            npc_id=npc_id,
            archetype=archetype,
            relationship_stage=relationship_stage,
            trust_score=trust_score,
            context=dialogue_context
        )
        
        if not dialogue:
            raise HTTPException(status_code=404, detail=f"No dialogue found for {npc_name} with archetype {archetype}")
        
        # Increment interaction count
        if isinstance(npc, dict):
            npc['interaction_count'] = interaction_count + 1
        else:
            npc.interaction_count = interaction_count + 1
        
        return {
            "npc_name": npc_name,
            "dialogue": dialogue,
            "archetype": archetype,
            "relationship_stage": relationship_stage.value,
            "trust_score": trust_score,
            "context": context
        }

    @router.get("/ship/state")
    async def get_ship_state(session_id: str = "default"):
        """Get the current state of the ship (zones, pressure, resources)."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        from src.narrative.ship_state import ShipStateManager
        
        state = sessions[session_id]
        ship_state_data = state.get("narrative_orchestrator", {}).orchestrator_data.get("ship_state", {})
        
        if ship_state_data:
            ship_manager = ShipStateManager.from_dict(ship_state_data)
        else:
            ship_manager = ShipStateManager()
        
        return {
            "zone_statuses": {k: v.value for k, v in ship_manager.zone_statuses.items()},
            "days_to_port": ship_manager.days_to_port,
            "fuel_level": ship_manager.fuel_level,
            "food_level": ship_manager.food_level,
            "air_quality": ship_manager.air_quality,
            "pressure_level": ship_manager._calculate_pressure(),
            "pressure_description": ship_manager.get_pressure_description(),
            "common_area_usage": ship_manager.common_area_usage
        }
    
    @router.post("/ship/event")
    async def trigger_ship_event(request: Dict[str, Any], session_id: str = "default"):
        """
        Trigger a ship event that changes environmental state.
        
        Request body:
        {
            "event": "murder_discovered",  # or tension_rises, violence_occurs, etc.
            "scene": 5
        }
        """
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        from src.narrative.ship_state import ShipStateManager, ShipEvent
        
        event_str = request.get("event")
        scene = request.get("scene", 0)
        
        if not event_str:
            raise HTTPException(status_code=400, detail="event required")
        
        try:
            event = ShipEvent(event_str)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event: {event_str}")
        
        # Get or create ship manager
        state = sessions[session_id]
        orch_state = state.get("narrative_orchestrator", {})
        ship_state_data = orch_state.orchestrator_data.get("ship_state", {})
        
        if ship_state_data:
            ship_manager = ShipStateManager.from_dict(ship_state_data)
        else:
            ship_manager = ShipStateManager()
        
        # Apply event
        changes = ship_manager.apply_event(event, scene)
        
        # Save back to state
        orch_state.orchestrator_data["ship_state"] = ship_manager.to_dict()
        
        return {
            "event": event.value,
            "changes": changes,
            "new_state": {
                "zone_statuses": {k: v.value for k, v in ship_manager.zone_statuses.items()},
                "pressure_level": ship_manager._calculate_pressure()
            }
        }

    @router.get("/premise")
    async def get_story_premise():
        """Get the locked story premise and designing principle."""
        from src.narrative.story_structure import get_story_structure
        structure = get_story_structure()
        return {
            "premise": structure.premise,
            "designing_principle": structure.designing_principle,
            "themes": structure.themes,
            "design_metaphors": structure.design_metaphors,
            "ironic_core": structure.ironic_core
        }

    @router.get("/character-web")
    async def get_character_web():
        """Get the character web with four-corner opposition."""
        from src.narrative.character_web import get_character_web
        return get_character_web()

    app.include_router(router)
