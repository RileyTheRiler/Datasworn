"""
Starforged AI Game Master - Backend Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env variables
load_dotenv()


# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_state import (
    create_initial_state, 
    GameState, 
    Character,
    NarrativeState
)
from src.narrator import generate_narrative, NarratorConfig
from src.image_gen import generate_location_image, generate_portrait
from src.director import DirectorAgent
from src.memory_system import MemoryPalace
from src.relationship_system import RelationshipWeb
from src.mystery_generator import MysteryConfig
from src.auto_save import AutoSaveSystem

app = FastAPI(title="Starforged AI GM")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. In prod, lock to frontend domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Assets Directory
ASSETS_DIR = Path("data/assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# In-memory session store (simple dict for single user for now)
# Key: session_id, Value: GameState
SESSIONS: Dict[str, GameState] = {}

# Global save system instance
SAVE_SYSTEM = AutoSaveSystem(save_directory="saves")

# Load Datasworn data for assets
from src.datasworn import load_starforged_data
try:
    DATASWORN = load_starforged_data()
except Exception:
    DATASWORN = None

class CharacterStatsInput(BaseModel):
    edge: int = 1
    heart: int = 2
    iron: int = 1
    shadow: int = 1
    wits: int = 2

class InitRequest(BaseModel):
    character_name: str
    background_vow: str = "Find my place among the stars"
    # Optional full character creation fields
    stats: Optional[CharacterStatsInput] = None
    asset_ids: Optional[list] = None  # List of asset names to equip
    background: Optional[str] = None  # Character background/description

class ActionRequest(BaseModel):
    session_id: str
    action: str

@app.get("/")
def health_check():
    return {"status": "online", "system": "Starforged AI GM"}

@app.get("/api/assets/available")
def get_available_assets():
    """Get all available assets for character creation."""
    if not DATASWORN:
        return {"assets": [], "error": "Datasworn not loaded"}
    
    assets_by_type = {}
    for asset in DATASWORN.get_all_assets():
        if asset.asset_type not in assets_by_type:
            assets_by_type[asset.asset_type] = []
        assets_by_type[asset.asset_type].append({
            "name": asset.name,
            "type": asset.asset_type,
            "abilities": asset.abilities[:2]  # First 2 abilities for preview
        })
    
    return {"assets": assets_by_type}

@app.post("/api/session/start")
def start_session(req: InitRequest):
    session_id = "default"  # Single session for MVP
    state = create_initial_state(req.character_name)
    
    # Apply custom stats if provided
    if req.stats:
        state['character'].stats.edge = max(1, min(3, req.stats.edge))
        state['character'].stats.heart = max(1, min(3, req.stats.heart))
        state['character'].stats.iron = max(1, min(3, req.stats.iron))
        state['character'].stats.shadow = max(1, min(3, req.stats.shadow))
        state['character'].stats.wits = max(1, min(3, req.stats.wits))
    
    # Apply custom assets if provided
    if req.asset_ids and DATASWORN:
        from src.game_state import AssetState
        for asset_name in req.asset_ids[:3]:  # Max 3 starting assets
            asset = DATASWORN.get_asset(asset_name)
            if asset:
                state['character'].assets.append(AssetState(
                    id=asset.id,
                    name=asset.name,
                    abilities_enabled=[True, False, False]
                ))
    
    # Apply custom background vow
    if req.background_vow:
        state['character'].vows[0].name = req.background_vow
    
    # Generate initial assets
    try:
        background_hint = req.background or "A gritty sci-fi survivor, determined expression"
        portrait_url = generate_portrait(req.character_name, background_hint)
    except Exception:
        portrait_url = None
    
    if not portrait_url:
        portrait_url = "/assets/defaults/portrait_placeholder.png"
    
    # Initialize Procedural Systems
    mystery = MysteryConfig()  # Randomly assigns "The Threat"
    state['mystery'].threat_id = mystery.threat_id
    state['mystery'].threat_motive = mystery.threat_motive
    state['mystery'].clues = [c.__dict__ for c in mystery.clues]
    
    relationships = RelationshipWeb()
    # Mark the threat in the relationship system
    if mystery.threat_id in relationships.crew:
        relationships.crew[mystery.threat_id].is_threat = True
    state['relationships'].crew = {k: v.to_dict() for k, v in relationships.crew.items()}
    
    SESSIONS[session_id] = state
    
    # Build personalized intro context
    asset_names = [a.name for a in state['character'].assets] if state['character'].assets else []
    asset_context = f"You are equipped with: {', '.join(asset_names)}." if asset_names else ""
    
    # Initial Narrative
    intro_narrative = generate_narrative(
        player_input="[Begin Game]",
        character_name=req.character_name,
        location="The Forge",
        context=f"The game begins. {req.background or 'You are a spacer in the Forge.'} {asset_context}",
        config=NarratorConfig(backend="gemini")
    )

    # Check for API failure in narrative
    if "[System: Rate Limit" in intro_narrative or "[Gemini error" in intro_narrative:
        intro_narrative = (
            "The neural link to the Oracle is unstable (API Rate Limit), but your localized systems are online.\n\n"
            "You stand in the hangar of **The Forge**. The air smells of ozone and rust. "
            "Your ship, the *Aethelgard*, sits dormant, waiting for repairs. "
            "A contact named Ira is expecting you at the sector hub.\n\n"
            "*Game started in Offline Fallback Mode. Images and dynamic text will resume when API quota resets.*"
        )

    
    state['narrative'].pending_narrative = intro_narrative
    state['narrative'].current_scene = "The Forge"
    
    return {
        "session_id": session_id,
        "state": state,
        "assets": {
            "portrait": portrait_url
        }
    }

@app.get("/api/psyche/{session_id}")
def get_psyche(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    psyche = state.get('psyche', {})
    
    # Return a merged dict for frontend compatibility if needed
    # but the profile object already has stress_level and sanity
    return psyche

@app.get("/api/state/{session_id}")
def get_state(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    return SESSIONS[session_id]

@app.get("/api/assets")
def list_assets():
    """List all available image assets."""
    assets = []
    if ASSETS_DIR.exists():
        for file in ASSETS_DIR.glob("*"):
            if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                assets.append(f"/assets/{file.name}")
    return {"assets": assets}

class SliceRequest(BaseModel):
    filename: str
    rows: Optional[int] = None
    cols: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    padding: int = 0

@app.post("/api/assets/slice")
def slice_asset(req: SliceRequest):
    """Slice a sprite sheet."""
    # 1. Locate file
    # Remove leading slash if present
    fname = req.filename.lstrip("/")
    # If it starts with assets/, remove that too if we are looking in ASSETS_DIR
    if fname.startswith("assets/"):
        fname = fname.replace("assets/", "", 1)
        
    file_path = ASSETS_DIR / fname
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Asset not found: {fname}")
        
    # 2. Slice
    from src.sprite_slicer import slice_spritesheet
    
    # Create a subfolder for slices or just list them? 
    # Let's create a subfolder: assets/{filename_stem}_sliced/
    output_dir = ASSETS_DIR / f"{file_path.stem}_sliced"
    
    try:
        slice_spritesheet(
            sheet_path=str(file_path),
            sprite_width=req.width,
            sprite_height=req.height,
            num_cols=req.cols,
            num_rows=req.rows,
            padding=req.padding,
            output_dir=str(output_dir)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slicing failed: {str(e)}")
        
    # 3. Return results
    sliced_files = []
    if output_dir.exists():
        for f in output_dir.glob("*.png"):
            sliced_files.append(f"/assets/{output_dir.name}/{f.name}")
            
    return {"created": sliced_files}

@app.post("/api/chat")
def chat(req: ActionRequest):
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    
    # 0. Hydrate Orchestrator & Director
    from src.narrative_orchestrator import NarrativeOrchestrator
    
    # Load Orchestrator
    orchestrator_data = state.get("narrative_orchestrator", {}).get("orchestrator_data", {})
    if orchestrator_data:
        orchestrator = NarrativeOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = NarrativeOrchestrator()
    
    # Director Analysis (Psychology & Pacing)
    director = DirectorAgent()
    director.inner_voice.sync_with_profile(state['psyche'].profile)
    for k, v in state['psyche'].voice_dominance.items():
        if k in director.inner_voice.aspects:
            director.inner_voice.aspects[k].dominance = v
            
    director.relationships = RelationshipWeb.from_dict(state['relationships'].dict())
            
    # Run analysis
    director_plan = director.analyze(
        world_state=state['world'].dict(),
        session_history=state['narrative'].pending_narrative
    )
    
    # Save back updated state
    for k, v in director.inner_voice.aspects.items():
        state['psyche'].voice_dominance[k] = v.dominance
        
    state['relationships'].crew = {k: v.to_dict() for k, v in director.relationships.crew.items()}
    
    # 1. Generate Narrative
    # Inject both Director Plan and Orchestrator Guidance
    director_injection = director_plan.to_prompt_injection()
    
    # Get active NPCs from world state (simple scan for now)
    active_npcs = [npc['name'] for npc in state['world'].npcs if npc.get('location') == state['world'].current_location]
    
    # Get Orchestrator Guidance (Bonds, Pacing, World Facts, etc.)
    orchestrator_guidance = orchestrator.get_comprehensive_guidance(
        location=state['world'].current_location,
        active_npcs=active_npcs,
        player_action=req.action
    )
    
    context_with_director = f"{state['narrative'].pending_narrative}\\n\\n{director_injection}\\n\\n{orchestrator_guidance}"
    
    narrative = generate_narrative(
        player_input=req.action,
        character_name=state['character'].name,
        location=state['world'].current_location,
        context=context_with_director, 
        config=NarratorConfig(backend="gemini"),
        psych_profile=state['psyche'].profile
    )
    
    # Update State
    state['narrative'].pending_narrative = narrative
    
    # 2. Process Interaction in Orchestrator (Updates Bonds, Facts, Plans)
    orchestrator.process_interaction(
        player_input=req.action,
        narrative_output=narrative,
        location=state['world'].current_location,
        active_npcs=active_npcs
    )
    
    # Save Orchestrator State
    state['narrative_orchestrator'].orchestrator_data = orchestrator.to_dict()
    
    # 3. Check for Location Change / Generate Visuals
    image_prompt = f"{state['world'].current_location}. {narrative[:100]}..."
    image_url = None
    try:
        filename = f"scene_{req.session_id}_{hash(narrative)}.png"
        image_url = generate_location_image(image_prompt, filename)
    except Exception as e:
        print(f"Image generation failed: {e}")

    return {
        "narrative": narrative,
        "state": state,
        "assets": {
            "scene_image": image_url
        }
    }

class RollCalculateRequest(BaseModel):
    stat: int
    adds: int = 0

class RollCommitRequest(BaseModel):
    session_id: str
    stat_name: str
    stat_val: int
    adds: int = 0
    move_name: str

@app.post("/api/roll/calculate")
def calculate_roll_odds(req: RollCalculateRequest):
    from src.rules_engine import calculate_probability
    return calculate_probability(req.stat, req.adds)

@app.post("/api/roll/commit")
def commit_roll(req: RollCommitRequest):
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    from src.rules_engine import action_roll
    
    # Perform the mechanics
    roll_result = action_roll(req.stat_val, req.adds)
    
    # Generate Narrative with the result
    outcome_map = {
        "Strong Hit": "strong_hit",
        "Weak Hit": "weak_hit",
        "Miss": "miss"
    }
    outcome_key = outcome_map[roll_result.result.value]
    
    # Construct input string for narrator
    action_desc = f"Attemping {req.move_name} using {req.stat_name}..."

    # Hydrate Orchestrator
    from src.narrative_orchestrator import NarrativeOrchestrator
    orchestrator_data = state.get("narrative_orchestrator", {}).get("orchestrator_data", {})
    if orchestrator_data:
        orchestrator = NarrativeOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = NarrativeOrchestrator()
    
    # Director Analysis
    director = DirectorAgent()
    director.inner_voice.sync_with_profile(state['psyche'].profile)
    for k, v in state['psyche'].voice_dominance.items():
        if k in director.inner_voice.aspects:
            director.inner_voice.aspects[k].dominance = v
    director.relationships = RelationshipWeb.from_dict(state['relationships'].dict())
    
    director_plan = director.analyze(
        world_state=state['world'].dict(), 
        session_history=state['narrative'].pending_narrative,
        player_action=action_desc,
        last_roll_outcome=outcome_key
    )
    
    # Save back updated state
    for k, v in director.inner_voice.aspects.items():
        state['psyche'].voice_dominance[k] = v.dominance
    state['relationships'].crew = {k: v.to_dict() for k, v in director.relationships.crew.items()}
    
    # Generate Context
    director_injection = director_plan.to_prompt_injection()
    
    active_npcs = [npc['name'] for npc in state['world'].npcs if npc.get('location') == state['world'].current_location]
    orchestrator_guidance = orchestrator.get_comprehensive_guidance(
        location=state['world'].current_location,
        active_npcs=active_npcs,
        player_action=action_desc
    )
    
    context_with_director = f"{state['narrative'].pending_narrative}\\n\\n{director_injection}\\n\\n{orchestrator_guidance}"
    
    narrative = generate_narrative(
        player_input=action_desc,
        roll_result=str(roll_result),
        outcome=outcome_key,
        character_name=state['character'].name,
        location=state['world'].current_location,
        context=context_with_director,
        config=NarratorConfig(backend="gemini"),
        psych_profile=state['psyche'].profile
    )
    
    # Update state history/pending narrative
    state['narrative'].pending_narrative = narrative
    
    # Process Interaction in Orchestrator
    orchestrator.process_interaction(
        player_input=action_desc,
        narrative_output=narrative,
        location=state['world'].current_location,
        active_npcs=active_npcs,
        roll_outcome=outcome_key
    )
    state['narrative_orchestrator'].orchestrator_data = orchestrator.to_dict()
    
    # Generate Visuals
    image_url = None
    try:
        image_prompt = f"Action scene: {req.move_name} in {state['world'].current_location}. Outcome: {outcome_key}. {narrative[:100]}..."
        filename = f"action_{req.session_id}_{hash(narrative)}.png"
        image_url = generate_location_image(image_prompt, filename)
    except Exception as e:
        print(f"Image generation failed: {e}")
    
    return {
        "roll": {
            "action_score": roll_result.action_score,
            "challenge_dice": roll_result.challenge_dice,
            "result": roll_result.result.value,
            "is_match": roll_result.is_match
        },
        "narrative": narrative,
        "state": state,
        "assets": {
            "scene_image": image_url
        }
    }

# ============================================================================
# Psychological System API Endpoints
# ============================================================================

from src.psych_profile import PsychologicalEngine
from src.difficulty_scaling import PsychologicalDifficultyScaler

class CopingRequest(BaseModel):
    session_id: str
    mechanism_id: str
    success: bool

class TherapyRequest(BaseModel):
    session_id: str
    scar_name: str

@app.post("/api/psyche/coping")
def apply_coping(req: CopingRequest):
    """Apply a coping mechanism to reduce stress."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    profile = state['psyche'].profile
    engine = PsychologicalEngine()
    
    result = engine.apply_coping_mechanism(profile, req.mechanism_id, req.success)
    
    # Save updated profile
    state['psyche'].profile = profile
    
    return {
        "result": result,
        "profile": profile.to_api_dict()
    }

@app.get("/api/psyche/available-coping/{session_id}")
def get_available_coping(session_id: str):
    """Get list of available coping mechanisms."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    profile = state['psyche'].profile
    
    return {
        "mechanisms": profile.get_available_coping_mechanisms()
    }

@app.post("/api/psyche/therapy")
def therapy_session(req: TherapyRequest):
    """Complete a therapy session for a specific trauma scar."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    profile = state['psyche'].profile
    engine = PsychologicalEngine()
    
    # Find the scar and increment therapy sessions
    for scar in profile.trauma_scars:
        if scar.name == req.scar_name:
            scar.therapy_sessions += 1
            break
    
    # Heal the scar
    heal_result = engine.heal_trauma_scar(profile, req.scar_name, progress=1.0)
    
    # Check for arc evolution
    arc_result = engine.evolve_trauma_arc(profile, req.scar_name)
    
    # Save updated profile
    state['psyche'].profile = profile
    
    return {
        "heal_result": heal_result,
        "arc_result": arc_result,
        "profile": profile.to_api_dict()
    }

@app.post("/api/psyche/check-breaking-point/{session_id}")
def check_breaking_point(session_id: str):
    """Check if character has hit a breaking point."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    profile = state['psyche'].profile
    engine = PsychologicalEngine()
    
    trauma = engine.check_breaking_point(profile)
    
    if trauma:
        state['psyche'].profile = profile
        return {
            "breaking_point": True,
            "trauma": trauma.model_dump(),
            "profile": profile.to_api_dict()
        }
    
    return {"breaking_point": False}

@app.get("/api/mystery/personalized/{session_id}")
def get_personalized_mystery(session_id: str):
    """Generate a mystery tailored to character's fears."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    profile = state['psyche'].profile
    
    mystery = MysteryConfig(threat_id="")
    mystery.generate_personalized_mystery(profile)
    
    # Update state
    state['mystery'].threat_id = mystery.threat_id
    state['mystery'].threat_motive = mystery.threat_motive
    state['mystery'].clues = [c.__dict__ for c in mystery.clues]
    
    return {
        "mystery": mystery.to_dict(),
        "fear": profile.get_primary_fear()
    }

@app.get("/api/difficulty/modifier/{session_id}")
def get_difficulty_modifier(session_id: str):
    """Get current difficulty modifier based on psychological state."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    profile = state['psyche'].profile
    scaler = PsychologicalDifficultyScaler()
    
    modifier = scaler.get_difficulty_modifier(profile)
    withdrawal = scaler.apply_withdrawal_penalty(profile)
    permadeath = scaler.check_permadeath(profile)
    
    return {
        "difficulty_modifier": modifier,
        "withdrawal_penalty": withdrawal,
        "permadeath": permadeath
    }


# ============================================================================
# Save/Load System API Endpoints
# ============================================================================

class SaveRequest(BaseModel):
    session_id: str
    slot_name: Optional[str] = None
    description: Optional[str] = ""

@app.get("/api/saves")
def list_saves():
    """List all available saves with metadata."""
    saves = SAVE_SYSTEM.list_saves()
    return {
        "saves": [s.to_dict() for s in saves]
    }

@app.post("/api/save")
def create_save(req: SaveRequest):
    """Create a manual save of the current game state."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    
    # Convert state to serializable format
    state_dict = {}
    for key, value in state.items():
        if hasattr(value, 'dict'):
            state_dict[key] = value.dict()
        elif hasattr(value, 'to_dict'):
            state_dict[key] = value.to_dict()
        else:
            state_dict[key] = value
    
    metadata = SAVE_SYSTEM.save_game(
        game_state=state_dict,
        slot_name=req.slot_name,
        description=req.description or "Manual save",
        is_auto=False
    )
    
    return {
        "success": True,
        "metadata": metadata.to_dict()
    }

@app.get("/api/save/{slot_name}")
def load_save(slot_name: str, version: int = 0):
    """Load a save from a specific slot."""
    state = SAVE_SYSTEM.load_game(slot_name, version)
    
    if state is None:
        raise HTTPException(status_code=404, detail=f"Save not found: {slot_name}")
    
    # Restore to session
    session_id = "default"
    SESSIONS[session_id] = state
    
    return {
        "success": True,
        "session_id": session_id,
        "state": state
    }

@app.delete("/api/save/{slot_name}")
def delete_save(slot_name: str):
    """Delete a save slot."""
    try:
        SAVE_SYSTEM.delete_save(slot_name)
        return {"success": True, "deleted": slot_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/save/recovery/check")
def check_recovery():
    """Check if crash recovery is available."""
    has_recovery = SAVE_SYSTEM.check_crash_recovery()
    info = SAVE_SYSTEM.get_recovery_info() if has_recovery else None
    
    return {
        "recovery_available": has_recovery,
        "info": info
    }

@app.post("/api/save/quicksave")
def quick_save(req: SaveRequest):
    """Quick save current game state."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    
    # Convert state to serializable format
    state_dict = {}
    for key, value in state.items():
        if hasattr(value, 'dict'):
            state_dict[key] = value.dict()
        elif hasattr(value, 'to_dict'):
            state_dict[key] = value.to_dict()
        else:
            state_dict[key] = value
    
    metadata = SAVE_SYSTEM.quick_save(state_dict)
    
    return {
        "success": True,
        "metadata": metadata.to_dict()
    }

@app.get("/api/save/quickload")
def quick_load():
    """Load the quick save slot."""
    state = SAVE_SYSTEM.quick_load()
    
    if state is None:
        raise HTTPException(status_code=404, detail="No quick save found")
    
    session_id = "default"
    SESSIONS[session_id] = state
    
    return {
        "success": True,
        "session_id": session_id,
        "state": state
    }


# ============================================================================
# Session Recap API Endpoints
# ============================================================================

from src.session_recap import SessionRecapEngine, RecapStyle

# Global recap engine instance
RECAP_ENGINE = SessionRecapEngine()

@app.get("/api/session/recap/{session_id}")
def get_session_recap(session_id: str, style: str = "dramatic"):
    """Generate a 'Previously on...' recap for the session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Map style string to enum
    style_map = {
        "dramatic": RecapStyle.DRAMATIC,
        "noir": RecapStyle.NOIR,
        "mysterious": RecapStyle.MYSTERIOUS,
        "urgent": RecapStyle.URGENT,
        "reflective": RecapStyle.REFLECTIVE,
    }
    recap_style = style_map.get(style.lower(), RecapStyle.DRAMATIC)
    
    state = SESSIONS[session_id]
    character_name = state['character'].name if hasattr(state['character'], 'name') else "You"
    
    recap = RECAP_ENGINE.get_recap_for_session_start(
        protagonist_name=character_name,
        style=recap_style
    )
    
    return {
        "recap": recap,
        "session_count": len(RECAP_ENGINE._session_history)
    }

@app.get("/api/session/story-so-far/{session_id}")
def get_story_so_far(session_id: str, length: str = "medium"):
    """Get a 'Story So Far' campaign summary."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    character_name = state['character'].name if hasattr(state['character'], 'name') else "the protagonist"
    
    # Extract active vows from state
    active_vows = []
    if hasattr(state, 'vows'):
        active_vows = [v.get('name', '') for v in state.get('vows', []) if v.get('active', True)]
    
    summary = RECAP_ENGINE.generate_story_so_far(
        protagonist_name=character_name,
        active_vows=active_vows,
        length=length
    )
    
    return {
        "summary": summary,
        "session_count": len(RECAP_ENGINE._session_history)
    }

class EndSessionRequest(BaseModel):
    session_id: str
    scene_description: Optional[str] = ""
    unresolved_tension: Optional[str] = ""

@app.post("/api/session/end")
def end_session_with_cliffhanger(req: EndSessionRequest):
    """End the current session and generate a cliffhanger."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    character_name = state['character'].name if hasattr(state['character'], 'name') else "you"
    
    # Generate cliffhanger if scene info provided
    cliffhanger = None
    if req.scene_description and req.unresolved_tension:
        cliffhanger = RECAP_ENGINE.generate_cliffhanger(
            final_scene=req.scene_description,
            unresolved_tension=req.unresolved_tension,
            protagonist_name=character_name
        )
    
    # End the session in the recap engine
    RECAP_ENGINE.end_session()
    
    return {
        "session_ended": True,
        "cliffhanger": cliffhanger,
        "total_sessions": len(RECAP_ENGINE._session_history)
    }

@app.post("/api/session/record-event")
def record_session_event(
    session_id: str,
    description: str,
    importance: int = 5,
    characters: Optional[str] = None,
    location: Optional[str] = None
):
    """Record a significant event for recap purposes."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    char_list = characters.split(",") if characters else []
    
    RECAP_ENGINE.record_event(
        description=description,
        importance=importance,
        characters=char_list,
        location=location or ""
    )
    
    return {"recorded": True}


# ============================================================================
# Export API Endpoints
# ============================================================================

from fastapi.responses import Response
from datetime import datetime

@app.get("/api/export/json/{session_id}")
def export_session_json(session_id: str):
    """Export the current game session as JSON."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Convert to serializable
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "session_id": session_id,
        "state": SAVE_SYSTEM._to_serializable(state)
    }
    
    import json
    json_content = json.dumps(export_data, indent=2, default=str)
    
    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=starforged_session_{session_id}.json"
        }
    )

@app.get("/api/export/story/{session_id}")
def export_story_markdown(session_id: str):
    """Export the narrative as a readable Markdown document."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Build markdown document
    character_name = state['character'].name if hasattr(state['character'], 'name') else "Unknown"
    location = state['world'].current_location if hasattr(state['world'], 'current_location') else "Unknown"
    narrative = state['narrative'].pending_narrative if hasattr(state['narrative'], 'pending_narrative') else ""
    
    # Get story so far from recap engine
    story_summary = RECAP_ENGINE.generate_story_so_far(
        protagonist_name=character_name,
        length="long"
    )
    
    md_content = f"""# Starforged: The Story of {character_name}

*Exported on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*

---

## Character
**Name:** {character_name}  
**Current Location:** {location}

---

## The Story So Far

{story_summary}

---

## Latest Scene

{narrative}

---

*Generated by Starforged AI Game Master*
"""
    
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=starforged_story_{character_name.lower().replace(' ', '_')}.md"
        }
    )

@app.get("/api/export/recap/{session_id}")
def export_recap(session_id: str):
    """Export just the recap text."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    character_name = state['character'].name if hasattr(state['character'], 'name') else "You"
    
    recap = RECAP_ENGINE.get_recap_for_session_start(
        protagonist_name=character_name,
        style=RecapStyle.DRAMATIC
    )
    
    return {"recap": recap}


def run():
    uvicorn.run("src.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
