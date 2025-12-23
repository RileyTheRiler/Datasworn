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
from src.image_gen import (
    generate_location_image, 
    generate_portrait, 
    PortraitStyle, 
    PortraitExpression,
    TimeOfDay,
    WeatherCondition
)
from src.director import DirectorAgent
from src.memory_system import MemoryPalace
from src.relationship_system import RelationshipWeb
from src.mystery_generator import MysteryConfig
from src.auto_save import AutoSaveSystem
from src.photo_album import PhotoAlbumManager
from src.psychology_api_models import *
from src.additional_api import register_starmap_routes, register_rumor_routes, register_audio_routes  # Added import

app = FastAPI(title="Starforged AI GM")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. In prod, lock to frontend domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (simple dict for single user for now)
# Key: session_id, Value: GameState
SESSIONS: Dict[str, GameState] = {}

# Mount Assets Directory
ASSETS_DIR = Path("data/assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Register additional API routes
register_starmap_routes(app, SESSIONS)
register_rumor_routes(app, SESSIONS)
register_audio_routes(app, SESSIONS)


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
    portrait_style: str = "realistic"

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
async def start_session(req: InitRequest):
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
        style = req.portrait_style if req.portrait_style in PortraitStyle.__members__.values() else PortraitStyle.REALISTIC
        state['character'].portrait_style = style
        
        portrait_url = await generate_portrait(
            character_name=req.character_name, 
            description=background_hint,
            style=style,
            expression=PortraitExpression.DETERMINED
        )
        if portrait_url:
            state['character'].image_url = portrait_url
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
    
    # Generate portraits for crew members
    crew_descriptions = {
        "captain": "Stern, weathered captain in their 50s. Gray at the temples, piercing eyes. Military bearing.",
        "engineer": "Asian engineer in grease-stained jumpsuit. Practical, focused expression. Mid-30s.",
        "medic": "African doctor in white coat. Calm, compassionate demeanor. Professional appearance.",
        "scientist": "Eastern European researcher with glasses. Intense, curious expression. Lab coat.",
        "security": "Hispanic security chief with buzz cut. Muscular build, alert stance. Tactical vest.",
        "pilot": "Androgynous pilot with short hair. Youthful, confident smirk. Flight suit.",
    }
    
    for crew_id, crew_member in relationships.crew.items():
        try:
            desc = crew_descriptions.get(crew_id, "Spacer in utilitarian clothing")
            crew_member.description = desc
            portrait_path = await generate_portrait(crew_member.name, f"{desc}. Gritty sci-fi portrait.")
            if portrait_path:
                crew_member.image_url = portrait_path
        except Exception as e:
            print(f"Failed to generate portrait for {crew_member.name}: {e}")
    
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
    
    # Hydrate Orchestrator to get Psychology data
    from src.narrative_orchestrator import NarrativeOrchestrator
    orchestrator_data = state.get("narrative_orchestrator", {}).get("orchestrator_data", {})
    if orchestrator_data:
        orchestrator = NarrativeOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = NarrativeOrchestrator()
    
    # Extract Phase 1-3 psychology data
    phobias = []
    for name, p in orchestrator.phobia_system.active_phobias.items():
        phobias.append({
            "name": p.name,
            "triggers": p.triggers,
            "panic": p.accumulated_panic,
            "severity": p.severity
        })
    
    addictions = []
    for sub, a in orchestrator.addiction_system.addictions.items():
        addictions.append({
            "substance": a.substance.value.upper(),
            "severity": a.severity,
            "satisfaction": a.satisfaction,
            "uses": a.uses
        })
    
    guilt = orchestrator.moral_injury_system.total_guilt
    
    # Merge into response
    if isinstance(psyche, dict):
        response = dict(psyche)
    elif hasattr(psyche, "model_dump"):
        response = psyche.model_dump()
    elif hasattr(psyche, "dict"):
        # Backward compatibility for Pydantic v1-style models
        response = psyche.dict()
    else:
        response = {}
    response["phobias"] = phobias
    response["addictions"] = addictions
    response["guilt"] = guilt
    
    return response

@app.get("/api/state/{session_id}")
def get_state(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    return SESSIONS[session_id]

@app.get("/api/npc/{npc_id}")
async def get_npc_data(npc_id: str, session_id: str = "default"):
    """Get NPC info for hover card display."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    relationships = state.get('relationships', {})
    crew = relationships.get('crew', {}) if isinstance(relationships, dict) else relationships.crew
    
    # Try to find NPC by id first, then by name
    npc = None
    if isinstance(crew, dict):
        # Check by id
        if npc_id.lower() in crew:
            npc = crew[npc_id.lower()]
        else:
            # Check by name (case-insensitive)
            for member_id, member in crew.items():
                member_name = member.get('name', '') if isinstance(member, dict) else member.name
                if member_name.lower() == npc_id.lower():
                    npc = member
                    break
    
    if not npc:
        raise HTTPException(status_code=404, detail=f"NPC not found: {npc_id}")
    
    # Extract fields (handle both dict and object)
    if isinstance(npc, dict):
        trust = npc.get('trust', 0.5)
        suspicion = npc.get('suspicion', 0.0)
        name = npc.get('name', npc_id)
        role = npc.get('role', 'Unknown')
        image_url = npc.get('image_url')
        description = npc.get('description', '')
        known_facts = npc.get('known_facts', [])[:5]
    else:
        trust = npc.trust
        suspicion = npc.suspicion
        name = npc.name
        role = npc.role
        image_url = npc.image_url if hasattr(npc, 'image_url') else None
        description = npc.description if hasattr(npc, 'description') else ''
        known_facts = npc.known_facts[:5] if npc.known_facts else []
    
    # Refresh portrait if missing
    if not image_url:
        image_url = await generate_portrait(
            character_name=name,
            description=description or f"A gritty {role.lower()}"
        )
        if isinstance(npc, dict):
            npc['image_url'] = image_url
        else:
            npc.image_url = image_url

    # Calculate disposition based on trust/suspicion
    if trust >= 0.7:
        disposition = "loyal"
    elif trust >= 0.5:
        disposition = "friendly"
    elif trust >= 0.3:
        disposition = "neutral"
    elif suspicion >= 0.6:
        disposition = "hostile"
    else:
        disposition = "suspicious"
    
    return {
        "name": name,
        "role": role,
        "trust": trust,
        "suspicion": suspicion,
        "disposition": disposition,
        "image_url": image_url or "/assets/defaults/portrait_placeholder.png",
        "description": description or f"A {role.lower()} aboard the vessel.",
        "known_facts": known_facts
    }

@app.get("/api/assets")
def list_assets():
    """List all available image assets."""
    assets = []
    if ASSETS_DIR.exists():
        for file in ASSETS_DIR.glob("*"):
            if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                assets.append(f"/assets/{file.name}")
    return {"assets": assets}

class PortraitRequest(BaseModel):
    name: str
    description: str
    style: str = "realistic"
    expression: str = "neutral"
    conditions: list[str] = []

@app.post("/api/assets/generate-portrait")
async def generate_custom_portrait(req: PortraitRequest):
    """Generate a custom portrait."""
    try:
        url = await generate_portrait(
            character_name=req.name,
            description=req.description,
            style=req.style,
            expression=req.expression,
            conditions=req.conditions
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

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
async def chat(req: ActionRequest):
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
    
    # 3. Check for Location Change / Generate Visuals with Environmental Conditions
    import random
    
    location = state['world'].current_location
    location_visuals = state['world'].location_visuals
    
    # Check if we have cached visuals for this location
    if location not in location_visuals:
        # Generate new environmental conditions
        time_options = [t.value for t in TimeOfDay]
        weather_options = [w.value for w in WeatherCondition]
        
        # Weighted random for more common conditions
        time_weights = [0.4, 0.2, 0.2, 0.2]  # Day, Night, Twilight, Dawn
        weather_weights = [0.5, 0.15, 0.15, 0.1, 0.05, 0.05]  # Clear, Rain, Dust Storm, Fog, Snow, Storm
        
        new_time = random.choices(time_options, weights=time_weights)[0]
        new_weather = random.choices(weather_options, weights=weather_weights)[0]
        
        # Update world state
        state['world'].current_time = new_time
        state['world'].current_weather = new_weather
        
        # Generate image with environmental conditions
        image_url = None
        try:
            description = narrative[:100] if narrative else "A mysterious location in the Forge"
            image_url = await generate_location_image(
                location_name=location,
                description=description,
                time_of_day=new_time,
                weather=new_weather
            )
        except Exception as e:
            print(f"Image generation failed: {e}")
        
        # Cache the visuals
        location_visuals[location] = {
            "time": new_time,
            "weather": new_weather,
            "image_url": image_url or "/assets/defaults/location_placeholder.png"
        }
    else:
        # Use cached visuals
        cached = location_visuals[location]
        state['world'].current_time = cached["time"]
        state['world'].current_weather = cached["weather"]
        image_url = cached["image_url"]

    # 4. NPC Voice Synthesis Integration
    voice_audio = None
    try:
        # Simple extraction for now: look for "NPC Name: \"Dialogue\""
        for npc_name in active_npcs:
            pattern = rf"{npc_name}:\s*\"([^\"]+)\""
            match = re.search(pattern, narrative)
            if match:
                dialogue = match.group(1)
                from src.voice_generator import VoiceGenerator
                from src.character_voice import VoiceManager
                
                # Get voice manager from state if exists, else create
                v_manager_data = state.get("voice_manager")
                if v_manager_data:
                    v_manager = VoiceManager.from_dict(v_manager_data)
                else:
                    v_manager = VoiceManager()
                
                profile = v_manager.get_character(npc_name)
                voice_profile = "default"
                if profile and profile.voice_id:
                    # If character has a specific voice_id, we'd need to update VoiceGenerator
                    # For now, let's map to archetype profiles in VoiceGenerator
                    # In a real app, VoiceGenerator should support dynamic IDs
                    pass 
                
                # Fallback to archetype-based voice
                generator = VoiceGenerator()
                # Find archetype from world npcs
                archetype = "default"
                for w_npc in state['world'].npcs:
                    if w_npc['name'] == npc_name:
                        archetype = w_npc.get('archetype', 'default')
                        break
                
                voice_audio = generator.generate_speech(dialogue, archetype)
                if voice_audio:
                    print(f"Generated voice for {npc_name}: {voice_audio}")
                break # Only generate one voice clip per turn for now
    except Exception as e:
        print(f"Voice synthesis failed in chat: {e}")

    return {
        "narrative": narrative,
        "state": state,
        "assets": {
            "scene_image": image_url,
            "voice_audio": voice_audio
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
async def commit_roll(req: RollCommitRequest):
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
        image_url = await generate_location_image(image_prompt, filename)
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

# ============================================================================
# Advanced Psychology API Endpoints (Phases 1-3)
# ============================================================================

from src.psychology_api_models import (
    AddPhobiaRequest, TriggerPhobiaRequest, UseSubstanceRequest,
    RecordTransgressionRequest, ForgiveTransgressionRequest,
    AdjustTrustRequest, RecordBetrayalRequest, TriggerDreamRequest
)
from src.psychology import SubstanceType, TransgressionType, BetrayalSeverity

def _get_orchestrator(session_id: str):
    """Helper to hydrate orchestrator from session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    from src.narrative_orchestrator import NarrativeOrchestrator
    orchestrator_data = state.get("narrative_orchestrator", {}).get("orchestrator_data", {})
    if orchestrator_data:
        return NarrativeOrchestrator.from_dict(orchestrator_data), state
    else:
        return NarrativeOrchestrator(), state

def _save_orchestrator(session_id: str, orchestrator):
    """Helper to save orchestrator back to session."""
    SESSIONS[session_id]['narrative_orchestrator'].orchestrator_data = orchestrator.to_dict()

@app.post("/api/psychology/phobia/add")
def add_phobia(req: AddPhobiaRequest):
    """Add a new phobia to the character."""
    orchestrator, state = _get_orchestrator(req.session_id)
    orchestrator.phobia_system.add_phobia(req.name, req.triggers, req.severity)
    _save_orchestrator(req.session_id, orchestrator)
    
    return {"success": True, "phobia": req.name}

@app.post("/api/psychology/phobia/trigger")
def trigger_phobia_check(req: TriggerPhobiaRequest):
    """Check narrative text for phobia triggers."""
    orchestrator, state = _get_orchestrator(req.session_id)
    panic_increase = orchestrator.phobia_system.check_triggers(req.narrative_text)
    panic_status = orchestrator.phobia_system.get_panic_status()
    _save_orchestrator(req.session_id, orchestrator)
    
    return {
        "panic_increase": panic_increase,
        "panic_status": panic_status,
        "active_phobias": [
            {"name": p.name, "panic": p.accumulated_panic}
            for p in orchestrator.phobia_system.active_phobias.values()
        ]
    }

@app.post("/api/psychology/addiction/use")
def use_substance(req: UseSubstanceRequest):
    """Character uses a substance."""
    orchestrator, state = _get_orchestrator(req.session_id)
    substance = SubstanceType(req.substance.lower())
    stress_relief = orchestrator.addiction_system.use_substance(substance)
    _save_orchestrator(req.session_id, orchestrator)
    
    # Apply stress relief to profile
    state['psyche'].profile.stress_level = max(0.0, state['psyche'].profile.stress_level - stress_relief)
    
    return {
        "success": True,
        "substance": req.substance,
        "stress_relief": stress_relief,
        "new_stress": state['psyche'].profile.stress_level
    }

@app.post("/api/psychology/transgression/record")
def record_transgression(req: RecordTransgressionRequest):
    """Record a moral transgression."""
    orchestrator, state = _get_orchestrator(req.session_id)
    t_type = TransgressionType(req.transgression_type.lower())
    orchestrator.moral_injury_system.record_transgression(t_type, req.description, req.weight)
    _save_orchestrator(req.session_id, orchestrator)
    
    return {
        "success": True,
        "total_guilt": orchestrator.moral_injury_system.total_guilt,
        "context": orchestrator.moral_injury_system.get_guilt_context()
    }

@app.post("/api/psychology/transgression/forgive")
def forgive_transgression(req: ForgiveTransgressionRequest):
    """Process/forgive a transgression."""
    orchestrator, state = _get_orchestrator(req.session_id)
    success = orchestrator.moral_injury_system.process_transgression(req.index)
    _save_orchestrator(req.session_id, orchestrator)
    
    return {
        "success": success,
        "total_guilt": orchestrator.moral_injury_system.total_guilt
    }

@app.post("/api/psychology/trust/adjust")
def adjust_trust(req: AdjustTrustRequest):
    """Adjust trust level with an NPC."""
    orchestrator, state = _get_orchestrator(req.session_id)
    orchestrator.trust_dynamics.adjust_trust(req.npc_id, req.delta)
    _save_orchestrator(req.session_id, orchestrator)
    
    return {
        "success": True,
        "npc_id": req.npc_id,
        "new_trust": orchestrator.trust_dynamics.get_trust(req.npc_id)
    }

@app.post("/api/psychology/betrayal/record")
def record_betrayal(req: RecordBetrayalRequest):
    """Record a betrayal event."""
    orchestrator, state = _get_orchestrator(req.session_id)
    severity = BetrayalSeverity(req.severity.lower())
    orchestrator.trust_dynamics.record_betrayal(req.betrayer_id, req.description, severity)
    _save_orchestrator(req.session_id, orchestrator)
    
    return {
        "success": True,
        "betrayer": req.betrayer_id,
        "new_trust": orchestrator.trust_dynamics.get_trust(req.betrayer_id)
    }

@app.post("/api/psychology/dream/trigger")
def trigger_dream(req: TriggerDreamRequest):
    """Generate a dream sequence."""
    orchestrator, state = _get_orchestrator(req.session_id)
    profile = state['psyche'].profile
    
    dream_text = orchestrator.dream_engine.generate_dream(
        recent_memories=req.recent_memories,
        suppressed_memories=req.suppressed_memories,
        dominant_emotion=profile.current_emotion,
        stress_level=profile.stress_level
    )
    
    return {
        "success": True,
        "dream": dream_text
    }



# ============================================================================
# Tactical Blueprint API
# ============================================================================

class BlueprintRequest(BaseModel):
    session_id: str
    force_regenerate: bool = False
    show_movement: bool = False
    show_vision: bool = False

@app.post("/api/blueprint")
async def generate_blueprint(req: BlueprintRequest):
    """Generate a tactical blueprint for the current location."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    
    # Import here to avoid circular dependencies
    from src.image_gen import generate_tactical_blueprint, clear_blueprint_cache
    
    if req.force_regenerate:
        clear_blueprint_cache()
    
    try:
        # Convert state to dict properly
        state_dict = {}
        for k, v in state.items():
            if hasattr(v, 'dict'):
                state_dict[k] = v.dict()
            else:
                state_dict[k] = v
        
        result = await generate_tactical_blueprint(
            state_dict, 
            show_movement=req.show_movement,
            show_vision=req.show_vision
        )
        
        return {
            "success": True,
            "blueprint": result["image_base64"],
            "metadata": result["metadata"],
            "cache_key": result.get("cache_key"),
            "from_cache": result.get("from_cache", False)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Ship Blueprint API
# ============================================================================

class ShipUpdateRequest(BaseModel):
    session_id: str
    hull_integrity: Optional[int] = None
    shield_integrity: Optional[int] = None
    active_alerts: Optional[list[str]] = None

@app.get("/api/ship/blueprint")
async def get_ship_blueprint(session_id: str, force_regenerate: bool = False):
    """Fetch the ship schematic blueprint."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    from src.image_gen import generate_ship_blueprint, clear_blueprint_cache
    
    if force_regenerate:
        clear_blueprint_cache()
        
    try:
        # Convert state to dict properly
        state_dict = {}
        for k, v in state.items():
            if hasattr(v, 'dict'):
                state_dict[k] = v.dict()
            else:
                state_dict[k] = v
                
        result = await generate_ship_blueprint(state_dict)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ship/update")
def update_ship_state(req: ShipUpdateRequest):
    """Update ship state (damage, alerts) for visualization."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    ship = state['world'].ship
    
    if req.hull_integrity is not None:
        ship.hull_integrity = req.hull_integrity
    if req.shield_integrity is not None:
        ship.shield_integrity = req.shield_integrity
    if req.active_alerts is not None:
        ship.active_alerts = req.active_alerts
        
    return {"success": True, "ship": ship.dict()}



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

# ============================================================================
# Photo Album API Endpoints
# ============================================================================

class CaptureRequest(BaseModel):
    session_id: str
    image_url: str
    caption: str
    tags: list[str] = []
    scene_id: str = ""

@app.get("/api/album")
def get_photo_album(session_id: str = "default"):
    """Get all photos in the album."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    album_state = state.get('album')
    
    # Handle both object and dict (Pydantic model in GameState)
    if hasattr(album_state, 'dict'):
        return album_state.dict()
    return album_state

@app.post("/api/album/capture")
async def capture_photo(req: CaptureRequest):
    """Manually capture a moment for the album."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    manager = PhotoAlbumManager(state['album'])
    
    entry = manager.capture_moment(
        image_url=req.image_url,
        caption=req.caption,
        tags=req.tags,
        scene_id=req.scene_id
    )
    
    return {"success": True, "photo": entry.dict() if hasattr(entry, 'dict') else entry}


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
# Ship Blueprint API Endpoints
# ============================================================================

class ShipBlueprintRequest(BaseModel):
    session_id: str
    force_regenerate: bool = False

class ShipUpdateRequest(BaseModel):
    session_id: str
    hull_damage: Optional[int] = None
    add_alert: Optional[str] = None
    clear_alerts: bool = False

@app.post("/api/ship/blueprint")
async def generate_ship_blueprint_endpoint(req: ShipBlueprintRequest):
    """Generate ship schematic blueprint."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    
    from src.image_gen import generate_ship_blueprint, clear_blueprint_cache
    
    if req.force_regenerate:
        clear_blueprint_cache()
    
    # Convert state to dict for processing
    state_dict = {}
    for k, v in state.items():
        if hasattr(v, 'dict'):
            state_dict[k] = v.dict()
        else:
            state_dict[k] = v
    
    try:
        result = await generate_ship_blueprint(state_dict)
        return {
            "blueprint": result["image_base64"],
            "metadata": result["metadata"],
            "from_cache": result.get("from_cache", False)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ship blueprint generation failed: {str(e)}")

@app.post("/api/ship/update")
def update_ship(req: ShipUpdateRequest):
    """Update ship state (for testing/gameplay)."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    ship = state['world'].ship
    
    if req.hull_damage is not None:
        ship.hull_integrity = max(0, ship.hull_integrity - req.hull_damage)
    
    if req.add_alert:
        if req.add_alert not in ship.active_alerts:
            ship.active_alerts.append(req.add_alert)
    
    if req.clear_alerts:
        ship.active_alerts = []
    
    return {
        "ship": ship.dict() if hasattr(ship, 'dict') else ship,
        "message": "Ship updated successfully"
    }


# ============================================================================
# Photo Album API Endpoints
# ============================================================================

class CaptureRequest(BaseModel):
    session_id: str
    image_url: str
    caption: str
    tags: list[str] = []
    scene_id: str = ""

@app.get("/api/album/{session_id}")
def get_album(session_id: str):
    """Get photo album for the session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    album_state = state.get("album")
    # If album state is missing (old save), initialize it
    if not album_state:
        from src.game_state import PhotoAlbumState
        state["album"] = PhotoAlbumState()
        album_state = state["album"]
        
    return {
        "photos": [p.dict() for p in album_state.photos]
    }

@app.post("/api/album/capture")
def capture_moment_api(req: CaptureRequest):
    """Manually capture a moment."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    album_state = state.get("album")
    if not album_state:
        from src.game_state import PhotoAlbumState
        state["album"] = PhotoAlbumState()
        album_state = state["album"]
    
    manager = PhotoAlbumManager(album_state)
    entry = manager.capture_moment(
        image_url=req.image_url,
        caption=req.caption,
        tags=req.tags,
        scene_id=req.scene_id
    )
    
    return {"success": True, "entry": entry.dict()}



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

from src.session_recap import MilestoneCategory, SessionRecapEngine, RecapStyle
from src.npc_templates import NPCRole, get_template, generate_quick_npc, get_all_roles, get_template_preview

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
    location: Optional[str] = None,
    category: Optional[str] = "narrative",
    timestamp: Optional[str] = None,
):
    """Record a significant event for recap purposes."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    char_list = characters.split(",") if characters else []

    parsed_timestamp = None
    if timestamp:
        try:
            parsed_timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            parsed_timestamp = None

    RECAP_ENGINE.record_event(
        description=description,
        importance=importance,
        characters=char_list,
        location=location or "",
        category=category,
        timestamp=parsed_timestamp,
    )

    return {"recorded": True}


@app.get("/api/session/timeline/{session_id}")
def get_timeline(session_id: str, categories: Optional[str] = None):
    """Return the recorded timeline with optional category filters."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    category_filter = [c.strip() for c in categories.split(",") if c.strip()] if categories else None
    entries = [entry.to_dict() for entry in RECAP_ENGINE.get_timeline(category_filter)]
    return {"timeline": entries, "total": len(entries)}


@app.get("/api/session/timeline/{session_id}/export")
def export_timeline(session_id: str, categories: Optional[str] = None):
    """Export a filtered timeline as JSON for sharing."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    category_filter = [c.strip() for c in categories.split(",") if c.strip()] if categories else None
    payload = RECAP_ENGINE.export_timeline_json(category_filter)
    return Response(content=payload, media_type="application/json")


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


# ============================================================================
# NPC Templates API Endpoints
# ============================================================================

@app.get("/api/npc/roles")
def get_npc_roles():
    """Get all available NPC role archetypes."""
    return {"roles": get_all_roles()}


@app.get("/api/npc/template/{role}")
def get_npc_template(role: str):
    """Get preview of a specific NPC template."""
    try:
        npc_role = NPCRole(role.lower())
        preview = get_template_preview(npc_role)
        if preview:
            return preview
        raise HTTPException(status_code=404, detail=f"Template not found: {role}")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")


class GenerateNPCRequest(BaseModel):
    role: str
    name: Optional[str] = None


@app.post("/api/npc/generate")
def generate_npc(req: GenerateNPCRequest):
    """Generate a quick NPC from a template."""
    try:
        npc_role = NPCRole(req.role.lower())
        npc = generate_quick_npc(npc_role, req.name)
        return {"npc": npc}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {req.role}")


@app.post("/api/npc/generate-random")
def generate_random_npc():
    """Generate a completely random NPC."""
    import random
    role = random.choice(list(NPCRole))
    npc = generate_quick_npc(role)
    return {"npc": npc}


# ============================================================================
# Quick Reference Commands API
# ============================================================================

QUICK_REFERENCE = {
    "moves": {
        "face_danger": {
            "name": "Face Danger",
            "stat": "Varies",
            "description": "When you attempt something risky or react to an imminent threat.",
            "strong_hit": "You succeed. Take +1 momentum.",
            "weak_hit": "You succeed but face a troublesome cost.",
            "miss": "You fail or your progress is undermined by a dramatic setback."
        },
        "secure_advantage": {
            "name": "Secure an Advantage",
            "stat": "Varies",
            "description": "When you assess a situation, make preparations, or position yourself for success.",
            "strong_hit": "You gain +2 momentum.",
            "weak_hit": "Take +1 momentum.",
            "miss": "You fail or your assumptions betray you."
        },
        "gather_information": {
            "name": "Gather Information",
            "stat": "Wits",
            "description": "When you search an area, ask questions, or investigate.",
            "strong_hit": "You discover something helpful and specific. Take +2 momentum.",
            "weak_hit": "The information complicates your quest or introduces a new danger.",
            "miss": "Your investigation reveals an unwelcome truth or triggers a perilous event."
        },
        "compel": {
            "name": "Compel",
            "stat": "Heart/Shadow/Iron",
            "description": "When you attempt to persuade or intimidate someone to do what you want.",
            "strong_hit": "They do what you want.",
            "weak_hit": "They do it but ask something in return.",
            "miss": "They refuse and your relationship worsens."
        },
        "aid_ally": {
            "name": "Aid Your Ally",
            "stat": "Varies",
            "description": "When you act in support of an ally.",
            "strong_hit": "They take +2 momentum.",
            "weak_hit": "Take +1 momentum each but you both face a cost.",
            "miss": "Your help fails and you both face the consequences."
        },
    },
    "stats": {
        "edge": "Quickness, agility, prowess in ranged combat",
        "heart": "Courage, willpower, empathy, sociability, loyalty",
        "iron": "Physical strength, endurance, prowess in close combat",
        "shadow": "Sneakiness, deceptiveness, cunning",
        "wits": "Expertise, knowledge, observation"
    },
    "momentum": {
        "description": "Momentum represents your character's luck, confidence, and preparation.",
        "reset": "Your momentum resets to +2 after you burn momentum.",
        "max": "Maximum momentum is +10.",
        "min": "Minimum momentum is -6.",
        "burn": "You can burn momentum to improve a roll result, but you cannot burn on a match."
    },
    "progress": {
        "troublesome": {"ticks_per_mark": 12, "description": "Easy challenges"},
        "dangerous": {"ticks_per_mark": 8, "description": "Moderate challenges"},
        "formidable": {"ticks_per_mark": 4, "description": "Hard challenges"},
        "extreme": {"ticks_per_mark": 2, "description": "Very hard challenges"},
        "epic": {"ticks_per_mark": 1, "description": "Legendary challenges"}
    }
}


@app.get("/api/reference")
def get_quick_reference():
    """Get the complete quick reference guide."""
    return QUICK_REFERENCE


@app.get("/api/reference/moves")
def get_moves_reference():
    """Get quick reference for all moves."""
    return {"moves": QUICK_REFERENCE["moves"]}


@app.get("/api/reference/move/{move_name}")
def get_move_reference(move_name: str):
    """Get quick reference for a specific move."""
    move = QUICK_REFERENCE["moves"].get(move_name.lower().replace(" ", "_"))
    if move:
        return move
    raise HTTPException(status_code=404, detail=f"Move not found: {move_name}")


@app.get("/api/reference/stats")
def get_stats_reference():
    """Get quick reference for all stats."""
    return {"stats": QUICK_REFERENCE["stats"]}


@app.get("/api/reference/momentum")
def get_momentum_reference():
    """Get quick reference for momentum rules."""
    return QUICK_REFERENCE["momentum"]


@app.get("/api/reference/progress")
def get_progress_reference():
    """Get quick reference for progress track ranks."""
    return {"progress": QUICK_REFERENCE["progress"]}


# ============================================================================
# Auto-Save Status Endpoint
# ============================================================================

@app.get("/api/autosave/status/{session_id}")
def get_autosave_status(session_id: str):
    """Get the current auto-save status."""
    # Check if there's a recent auto-save
    saves = SAVE_SYSTEM.list_saves()
    auto_saves = [s for s in saves if s.is_auto]

    if auto_saves:
        latest = auto_saves[0]
        return {
            "enabled": True,
            "last_save": latest.timestamp,
            "slot": latest.slot_name,
            "description": latest.description
        }

    return {
        "enabled": True,
        "last_save": None,
        "slot": None,
        "description": "No auto-saves yet"
    }




# ============================================================================
# Audio & Voice API Endpoints
# ============================================================================

from src.audio_engine import AudioEngine
from src.voice_generator import VoiceGenerator

# Initialize voice generator
VOICE_GENERATOR = VoiceGenerator()

class TTSRequest(BaseModel):
    session_id: str
    text: str
    character_archetype: str = "default"
    use_cache: bool = True

@app.get("/api/audio/state/{session_id}")
def get_audio_state(session_id: str):
    """Get current audio directives for the game state."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Create audio engine from saved state
    audio_data = state.get('audio', {})
    if isinstance(audio_data, dict):
        engine = AudioEngine.from_dict(audio_data)
    else:
        engine = AudioEngine.from_dict(audio_data.dict() if hasattr(audio_data, 'dict') else {})
    
    # Get current directives
    directives = engine.get_audio_directives(
        location=state['world'].current_location,
        location_type=state['world'].location_type,
        tension=state['director'].tension_level,
        combat_active=state['world'].combat_active
    )
    
    return directives

@app.post("/api/audio/tts")
def generate_tts(req: TTSRequest):
    """Generate TTS audio for dialogue."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        audio_url = VOICE_GENERATOR.generate_speech(
            text=req.text,
            voice_profile=req.character_archetype,
            use_cache=req.use_cache
        )
        
        if audio_url:
            return {"audio_url": audio_url, "cached": req.use_cache}
        else:
            return {"audio_url": None, "error": "TTS generation failed or API unavailable"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation error: {str(e)}")

class VolumeRequest(BaseModel):
    session_id: str
    channel: str  # "ambient", "music", "voice", "master"
    volume: float  # 0.0-1.0

@app.post("/api/audio/volume")
def set_volume(req: VolumeRequest):
    """Set volume for a specific audio channel."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    
    # Update audio state
    audio_data = state.get('audio', {})
    if isinstance(audio_data, dict):
        engine = AudioEngine.from_dict(audio_data)
    else:
        engine = AudioEngine.from_dict(audio_data.dict() if hasattr(audio_data, 'dict') else {})
    
    engine.set_volume(req.channel, req.volume)
    
    # Save back to state
    state['audio'] = engine.state
    
    return {"success": True, "channel": req.channel, "volume": req.volume}

@app.post("/api/audio/mute/{session_id}")
def toggle_mute(session_id: str):
    """Toggle mute state."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Update audio state
    audio_data = state.get('audio', {})
    if isinstance(audio_data, dict):
        engine = AudioEngine.from_dict(audio_data)
    else:
        engine = AudioEngine.from_dict(audio_data.dict() if hasattr(audio_data, 'dict') else {})
    
    muted = engine.toggle_mute()
    
    # Save back to state
    state['audio'] = engine.state
    
    return {"muted": muted}


def run():
    uvicorn.run("src.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
