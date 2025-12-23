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
from src.narrative.choice_crystallized import ChoiceCrystallizedSystem
from src.narrative.mirror_moment import MirrorMomentSystem
from src.character_identity import WoundType
from src.narrative.reyes_journal import ReyesJournalSystem
from src.additional_api import register_starmap_routes, register_rumor_routes
from src.narrative_api import register_narrative_routes
from src.psych_api import register_psychology_routes
from src.combat_api import register_combat_routes
from src.practice_api import register_practice_routes
from src.calibration import get_calibration_scenario
from src.npc.schemas import CognitiveState, PersonalityProfile
from src.npc.engine import NPCCognitiveEngine
from src.quickstart_characters import get_quickstart_characters, get_quickstart_character_by_id
from src.narrative_templates import get_all_templates, get_suggested_vows_for_path
from src.story_templates import get_story_templates, get_story_template_by_id

app = FastAPI(title="Starforged AI GM")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
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
register_narrative_routes(app, SESSIONS)
register_psychology_routes(app, SESSIONS)
register_combat_routes(app, SESSIONS)
register_practice_routes(app)

# Register archetype system routes
from src.archetype_api import register_archetype_routes
register_archetype_routes(app, SESSIONS)

# Register NPC scheduling routes
from src.npc_scheduling_api import register_npc_scheduling_routes
register_npc_scheduling_routes(app, SESSIONS)

# Register quest system routes
from src.quest_api import register_quest_routes
register_quest_routes(app, SESSIONS)

# Register camp system routes
from src.camp_api import register_camp_routes
register_camp_routes(app, SESSIONS)

# Register world simulation routes
from src.world_api import register_world_routes
register_world_routes(app, SESSIONS)

# Register faction routes
from src.faction_api import register_faction_routes
register_faction_routes(app, SESSIONS)



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
    character_name: str = ""
    background_vow: str = "Find my place among the stars"
    # Optional full character creation fields
    stats: Optional[CharacterStatsInput] = None
    asset_ids: Optional[list] = None  # List of asset names to equip
    background: Optional[str] = None  # Character background/description
    portrait_style: str = "realistic"
    # Quick-start character support
    quickstart_id: Optional[str] = None  # If provided, use a pre-built character
    # Story template support
    story_template_id: Optional[str] = None  # If provided, use a pre-built story setting

class ActionRequest(BaseModel):
    session_id: str
    action: str

@app.get("/")
def health_check():
    return {"status": "online", "system": "Starforged AI GM"}

@app.get("/api/health")
def api_health_check():
    """Health check endpoint for startup verification."""
    return {"status": "online", "system": "Starforged AI GM", "version": "0.9.1"}

@app.post("/api/shutdown")
async def shutdown():
    """Gracefully shutdown the server and close terminal windows."""
    import os
    import signal
    import subprocess
    
    def cleanup_and_shutdown():
        # Kill the server processes which will close their terminal windows
        try:
            # Kill uvicorn processes (more specific than all python.exe)
            subprocess.run(
                ['taskkill', '/F', '/FI', 'IMAGENAME eq python.exe', '/FI', 'WINDOWTITLE ne N/A'],
                capture_output=True,
                timeout=2
            )
        except Exception as e:
            print(f"Failed to kill backend process: {e}")
        
        try:
            # Kill node processes running dev server
            subprocess.run(
                ['taskkill', '/F', '/FI', 'IMAGENAME eq node.exe', '/FI', 'WINDOWTITLE ne N/A'],
                capture_output=True,
                timeout=2
            )
        except Exception as e:
            print(f"Failed to kill frontend process: {e}")
        
        try:
            # Also kill the cmd.exe processes that spawned them
            subprocess.run(
                ['taskkill', '/F', '/FI', 'IMAGENAME eq cmd.exe', '/FI', 'WINDOWTITLE eq *Starforged*'],
                capture_output=True,
                timeout=2
            )
        except Exception as e:
            print(f"Failed to kill cmd windows: {e}")
        
        # Finally, kill this process (redundant but ensures cleanup)
        try:
            os.kill(os.getpid(), signal.SIGTERM)
        except:
            pass
    
    # Schedule cleanup and shutdown after response is sent
    import asyncio
    asyncio.get_event_loop().call_later(0.5, cleanup_and_shutdown)
    
    return {"status": "shutting down", "message": "Closing all terminals and stopping servers..."}

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

@app.get("/api/quickstart/characters")
def get_quickstart_character_list():
    """Get all available quick-start character presets."""
    return {"characters": get_quickstart_characters()}

@app.get("/api/narrative/templates")
def get_narrative_templates():
    """Get all narrative templates organized by category."""
    return {"templates": get_all_templates()}

@app.get("/api/narrative/vows/{path_name}")
def get_vows_for_path(path_name: str):
    """Get suggested vows for a specific character path."""
    vows = get_suggested_vows_for_path(path_name)
    return {"path": path_name, "suggested_vows": vows}

@app.get("/api/story/templates")
def get_story_template_list():
    """Get all available story templates/settings."""
    return {"templates": get_story_templates()}

@app.post("/api/session/start")
async def start_session(req: InitRequest):
    session_id = "default"  # Single session for MVP

    # Handle quick-start character
    if req.quickstart_id:
        quickstart_char = get_quickstart_character_by_id(req.quickstart_id)
        if not quickstart_char:
            raise HTTPException(status_code=404, detail=f"Quick-start character '{req.quickstart_id}' not found")

        # Use quick-start character data
        state = create_initial_state(quickstart_char.name)

        # Apply quick-start stats
        state['character'].stats.edge = quickstart_char.stats.edge
        state['character'].stats.heart = quickstart_char.stats.heart
        state['character'].stats.iron = quickstart_char.stats.iron
        state['character'].stats.shadow = quickstart_char.stats.shadow
        state['character'].stats.wits = quickstart_char.stats.wits

        # Apply quick-start assets
        if DATASWORN:
            from src.game_state import AssetState
            for asset_name in quickstart_char.asset_ids[:3]:
                asset = DATASWORN.get_asset(asset_name)
                if asset:
                    state['character'].assets.append(AssetState(
                        id=asset.id,
                        name=asset.name,
                        abilities_enabled=[True, False, False]
                    ))

        # Apply quick-start vow and background
        state['character'].vows[0].name = quickstart_char.vow
        req.background = quickstart_char.background_story
        req.background_vow = quickstart_char.vow
        req.character_name = quickstart_char.name

        # Store special mechanics in narrative state
        if quickstart_char.special_mechanics:
            state['narrative'].campaign_summary = f"Special Character Mechanics: {quickstart_char.special_mechanics}\n\n"
            state['narrative'].session_summary = quickstart_char.starting_scene
    else:
        # Regular character creation
        state = create_initial_state(req.character_name)

    # Apply custom stats if provided (and not using quick-start)
    if req.stats and not req.quickstart_id:
        state['character'].stats.edge = max(1, min(3, req.stats.edge))
        state['character'].stats.heart = max(1, min(3, req.stats.heart))
        state['character'].stats.iron = max(1, min(3, req.stats.iron))
        state['character'].stats.shadow = max(1, min(3, req.stats.shadow))
        state['character'].stats.wits = max(1, min(3, req.stats.wits))
    
    # Apply custom assets if provided (and not using quick-start)
    if req.asset_ids and DATASWORN and not req.quickstart_id:
        from src.game_state import AssetState
        for asset_name in req.asset_ids[:3]:  # Max 3 starting assets
            asset = DATASWORN.get_asset(asset_name)
            if asset:
                state['character'].assets.append(AssetState(
                    id=asset.id,
                    name=asset.name,
                    abilities_enabled=[True, False, False]
                ))

    # Apply custom background vow (unless quick-start already set it)
    if req.background_vow and not req.quickstart_id:
        state['character'].vows[0].name = req.background_vow

    # Handle story template selection
    if req.story_template_id:
        story_template = get_story_template_by_id(req.story_template_id)
        if not story_template:
            raise HTTPException(status_code=404, detail=f"Story template '{req.story_template_id}' not found")

        # Set starting location
        state['world'].current_location = story_template.starting_location
        state['world'].location_type = story_template.setting_type

        # Set opening scene in narrative state
        state['narrative'].current_scene = story_template.opening_scene

        # Store story template info in campaign summary
        story_context = (
            f"Story Setting: {story_template.name}\n"
            f"{story_template.tagline}\n\n"
            f"Setting Type: {story_template.setting_type}\n"
            f"Starting Location: {story_template.starting_location}\n\n"
            f"Initial Scenario: {story_template.initial_scenario}\n\n"
            f"Tone: {story_template.tone}\n"
            f"Difficulty: {story_template.difficulty}\n\n"
            f"Themes: {', '.join(story_template.suggested_themes)}\n\n"
            f"Environmental Conditions:\n"
        )
        for condition, value in story_template.environmental_conditions.items():
            story_context += f"  - {condition.title()}: {value}\n"

        # Append to existing campaign summary or create new one
        if state['narrative'].campaign_summary:
            state['narrative'].campaign_summary += "\n\n" + story_context
        else:
            state['narrative'].campaign_summary = story_context

        # Set environmental visuals if available
        state['world'].current_time = story_template.environmental_conditions.get("lighting", "Day")
        state['world'].current_weather = story_template.environmental_conditions.get("atmosphere", "Clear")

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
    
    for crew_id, crew_member in relationships.crew.items():
        try:
            # Use description from psyche if available, otherwise fallback
            desc = None
            if hasattr(crew_member, 'psyche') and crew_member.psyche:
                if isinstance(crew_member.psyche, dict):
                    desc = crew_member.psyche.get('description')
                else:
                    desc = getattr(crew_member.psyche, 'description', None)
            
            if not desc:
                crew_descriptions = {
                    "captain": "Stern, weathered captain in their 50s. Gray at the temples, piercing eyes. Military bearing.",
                    "engineer": "Chief Engineer. Addiction issues; Reyes hoped the ship's structure would help him recover.",
                    "medic": "The Medic. Past medical scandal; Reyes offered her a second chance. She knew he was dying.",
                    "scientist": "Security Officer (37). Professional, quiet, and reliable. Formerly a Corporate Enforcer for Helix Dynamics.",
                    "security": "Security Officer (37). Professional, quiet, and reliable. Formerly a Corporate Enforcer for Helix Dynamics.",
                    "pilot": "The Pilot. Former military, court-martialed for disobeying orders to save lives. Reyes saw himself in her.",
                    "apprentice": "The Apprentice. Stowaway runaway; Reyes would have mentored her if he'd lived.",
                    "cargo": "The Cargo Master. Criminal past; needed to disappear. Reyes believed in redemption for everyone.",
                }
                desc = crew_descriptions.get(crew_id, "Spacer in utilitarian clothing")
            
            crew_member.description = desc
            portrait_path = await generate_portrait(crew_member.name, f"{desc}. Gritty sci-fi portrait.")
            if portrait_path:
                crew_member.image_url = portrait_path
        except Exception as e:
            print(f"Failed to generate portrait for {crew_member.name}: {e}")
    
    state['relationships'].crew = {k: v.to_dict() for k, v in relationships.crew.items()}
    
    # Initialize Cognitive State for Crew
    from src.npc.schemas import CognitiveState, PersonalityProfile
    for crew_id, crew_member in relationships.crew.items():
        # Map CrewMember to PersonalityProfile
        try:
             # Safety check for psyche access
             archetype = "Stoic"
             if hasattr(crew_member, 'psyche') and crew_member.psyche:
                 if isinstance(crew_member.psyche, dict):
                     archetype = crew_member.psyche.get('personality_archetype', "Stoic")
                 else:
                     archetype = getattr(crew_member.psyche, 'personality_archetype', "Stoic")
             
             profile = PersonalityProfile(
                name=crew_member.name,
                role=crew_member.role,
                traits=[archetype],
                narrative_seed=f"{crew_member.name} is the {crew_member.role} of the Aethelgard. {crew_member.description}",
                current_mood="Neutral"
            )
             # Create State
             cog_state = CognitiveState(npc_id=crew_id, profile=profile)
             state['cognitive_npc_state'][crew_id] = cog_state
             # Also map by name for easier lookup
             state['cognitive_npc_state'][crew_member.name] = cog_state
        except Exception as e:
            print(f"Warning: Failed to init cognitive state for {crew_id}: {e}")

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
    
    # Generate initial location visuals
    import random
    location = state['narrative'].current_scene
    location_visuals = state['world'].location_visuals
    
    # Generate environmental conditions
    time_options = [t.value for t in TimeOfDay]
    weather_options = [w.value for w in WeatherCondition]
    
    new_time = random.choices(time_options, weights=[0.4, 0.2, 0.2, 0.2])[0]
    new_weather = random.choices(weather_options, weights=[0.5, 0.15, 0.15, 0.1, 0.05, 0.05])[0]
    
    state['world'].current_time = new_time
    state['world'].current_weather = new_weather
    
    scene_image = None
    try:
        scene_image = await generate_location_image(
            location_name=location,
            description=intro_narrative[:100],
            time_of_day=new_time,
            weather=new_weather
        )
    except Exception as e:
        print(f"Initial scene generation failed: {e}")
        
    location_visuals[location] = {
        "time": new_time,
        "weather": new_weather,
        "image_url": scene_image or "/assets/defaults/location_placeholder.png"
    }
    
    return {
        "session_id": session_id,
        "state": state,
        "assets": {
            "portrait": portrait_url,
            "scene_image": scene_image or "/assets/defaults/location_placeholder.png"
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
    
    # Explicitly serialize archetype_profile using its to_dict method which has computed props
    if hasattr(psyche, 'archetype_profile') and psyche.archetype_profile:
        # Check if it has to_dict (it should)
        if hasattr(psyche.archetype_profile, 'to_dict'):
             response['archetype_profile'] = psyche.archetype_profile.to_dict()
    
    response["phobias"] = phobias
    response["addictions"] = addictions
    response["guilt"] = guilt
    
    return response

@app.get("/api/identity/{session_id}")
def get_identity(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    return state['psyche'].profile.identity.to_dict()

@app.get("/api/calibration/scenario")
def get_prologue_scenario():
    return get_calibration_scenario()

class CalibrateRequest(BaseModel):
    session_id: str
    choice_id: str

@app.post("/api/calibrate")
async def calibrate_identity(req: CalibrateRequest):
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
        
    state = SESSIONS[req.session_id]
    scenario = get_calibration_scenario()
    
    choice = next((c for c in scenario['choices'] if c['id'] == req.choice_id), None)
    if not choice:
        raise HTTPException(status_code=400, detail="Invalid choice ID")
        
    # Apply impact
    from src.character_identity import IdentityScore
    impact = IdentityScore(**choice['impact'] if isinstance(choice['impact'], dict) else choice['impact'].to_dict())
    state['psyche'].profile.identity.update_scores(impact, f"Calibration Choice: {choice['text']}")
    
    # NEW: Also seed the Archetype Profile (Phase 4)
    if not state['psyche'].archetype_profile:
        from src.narrative.archetype_types import ArchetypeProfile
        state['psyche'].archetype_profile = ArchetypeProfile()
        
    ap = state['psyche'].archetype_profile
    
    # Map IdentityScore fields to Archetypes
    # Values in impact are typically 0.1 to 0.5
    if impact.violence > 0:
        ap.destroyer += impact.violence * 0.6
        ap.avenger += impact.violence * 0.4
    if impact.stealth > 0:
        ap.fugitive += impact.stealth * 0.5
        ap.ghost += impact.stealth * 0.5
    if impact.empathy > 0:
        ap.savior += impact.empathy * 0.5
        ap.martyr += impact.empathy * 0.5
    if impact.logic > 0:
        ap.controller += impact.logic * 0.5
        ap.pedant += impact.logic * 0.5
    if impact.greed > 0:
        ap.hedonist += impact.greed * 0.5
        ap.manipulator += impact.greed * 0.5
    
    # Update observation count to boost confidence slightly
    ap.observation_count += 3
    
    return {
        "identity": state['psyche'].profile.identity.to_dict(),
        "hint": choice['narrative_hint']
    }

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
    
    npc = None
    is_world_npc = False

    # 1. Search in Crew
    if isinstance(crew, dict):
        if npc_id.lower() in crew:
            npc = crew[npc_id.lower()]
        else:
            for member_id, member in crew.items():
                member_name = member.get('name', '') if isinstance(member, dict) else member.name
                if member_name.lower() == npc_id.lower():
                    npc = member
                    break
    
    # 2. Search in World NPCs if not found in Crew
    if not npc:
        world_npcs = state['world'].npcs
        for w_npc in world_npcs:
            if w_npc.get('name', '').lower() == npc_id.lower() or w_npc.get('id', '').lower() == npc_id.lower():
                npc = w_npc
                is_world_npc = True
                break

    if not npc:
        raise HTTPException(status_code=404, detail=f"NPC not found: {npc_id}")
    
    # Extract fields
    if not is_world_npc:
        # Crew Member
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
    else:
        # World NPC (always dict)
        trust = npc.get('trust', 0.5) # Default to neutral
        suspicion = npc.get('suspicion', 0.0)
        name = npc.get('name', npc_id)
        role = npc.get('role', npc.get('archetype', 'Unknown'))
        image_url = npc.get('image_url')
        description = npc.get('description', npc.get('narrative_role', ''))
        known_facts = [] # World NPCs might not have structured known_facts yet

    # Refresh portrait if missing
    if not image_url:
        print(f"Generating missing portrait for {name}...")
        try:
            image_url = await generate_portrait(
                character_name=name,
                description=description or f"A gritty {role.lower()}"
            )
            
            # Update state with new image
            if not is_world_npc:
                if isinstance(npc, dict):
                    npc['image_url'] = image_url
                else:
                    npc.image_url = image_url
            else:
                npc['image_url'] = image_url
                
        except Exception as e:
            print(f"Failed to generate lazy portrait for {name}: {e}")
            image_url = "/assets/defaults/portrait_placeholder.png"

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
        "description": description or f"A {role.lower()} encounter.",
        "known_facts": known_facts
    }

@app.get("/api/npc/{npc_id}/archetype_response")
async def get_npc_archetype_response(npc_id: str, session_id: str = "default"):
    """Get NPC's specific response based on player's current archetype (WoundType)."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get player's dominant wound/archetype
    player_wound = state['psyche'].profile.identity.wound_profile.dominant_wound
    player_wound_str = player_wound.value if hasattr(player_wound, 'value') else str(player_wound)
    
    # Get RelationshipWeb
    relationships_data = state.get('relationships', {})
    if hasattr(relationships_data, 'model_dump'):
        relationships = RelationshipWeb.from_dict(relationships_data.model_dump())
    elif isinstance(relationships_data, dict):
        relationships = RelationshipWeb.from_dict(relationships_data)
    else:
        relationships = relationships_data
    
    # Get response
    response_text = relationships.get_npc_archetype_response(npc_id, player_wound_str)
    
    return {
        "npc_id": npc_id,
        "player_archetype": player_wound_str,
        "response": response_text
    }

@app.post("/api/npc/generate-all")
async def generate_all_npc_portraits(session_id: str = "default"):
    """Trigger generation for all NPCs missing portraits."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
        
    state = SESSIONS[session_id]
    generated_count = 0
    errors = []
    
    # Collect all NPCs needing images
    targets = []
    
    # 1. Crew
    relationships = state['relationships']
    crew = relationships.get('crew', {}) if isinstance(relationships, dict) else relationships.crew
    
    crew_items = crew.items() if isinstance(crew, dict) else [(c.id, c) for c in crew.values()]
    
    for _, npc in crew_items:
        img = npc.get('image_url') if isinstance(npc, dict) else getattr(npc, 'image_url', None)
        if not img:
            name = npc.get('name') if isinstance(npc, dict) else npc.name
            desc = npc.get('description') if isinstance(npc, dict) else getattr(npc, 'description', "")
            targets.append((npc, name, desc or f"Crew member {name}"))

    # 2. World NPCs
    for npc in state['world'].npcs:
        if not npc.get('image_url'):
            targets.append((npc, npc['name'], npc.get('description', npc.get('role', 'NPC'))))
            
    # Generate concurrently
    import asyncio
    
    async def _gen_and_assign(target_tuple):
        npc_obj, name, desc = target_tuple
        try:
            url = await generate_portrait(name, desc)
            if url:
                if isinstance(npc_obj, dict):
                    npc_obj['image_url'] = url
                else:
                    npc_obj.image_url = url
                return True
        except Exception as e:
            return f"Failed {name}: {e}"
        return False

    if targets:
        print(f"Batch generating {len(targets)} portraits...")
        results = await asyncio.gather(*[_gen_and_assign(t) for t in targets])
        
        for r in results:
            if r is True:
                generated_count += 1
            elif r:
                errors.append(str(r))
                
    return {
        "generated": generated_count,
        "total_targets": len(targets),
        "errors": errors
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

@app.get("/api/music/manifest")
def get_music_manifest():
    """Get all available music tracks organized by mood."""
    music_dir = ASSETS_DIR / "music"
    manifest = {
        "theme": [],
        "relaxing": [],
        "tense": [],
        "dramatic": [],
        "intense": []
    }
    
    if music_dir.exists():
        for mood in manifest.keys():
            mood_dir = music_dir / mood
            if mood_dir.exists():
                for file in mood_dir.glob("*"):
                    if file.suffix.lower() in ['.mp3', '.wav', '.ogg', '.m4a']:
                        manifest[mood].append(f"/assets/music/{mood}/{file.name}")
    
    return manifest

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
    
@app.get("/api/combat/debug/{session_id}")
def get_combat_debug(session_id: str):
    """Get attack grid and token status for debugging."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Hydrate Orchestrator
    from src.narrative_orchestrator import NarrativeOrchestrator
    orchestrator_data = state.get("narrative_orchestrator", {}).get("orchestrator_data", {})
    if orchestrator_data:
        orchestrator = NarrativeOrchestrator.from_dict(orchestrator_data)
        if orchestrator.combat_system:
            return orchestrator.combat_system.to_dict()
            
    return {"status": "No active combat system"}

@app.post("/api/chat")
async def chat(req: ActionRequest):
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]

    # --- NEW: Update Psychological Profile (Wounds/RUO) ---
    try:
        from src.psych_profile import PsychologicalEngine
        psych_engine = PsychologicalEngine()
        psych_engine.update_wound_profile(state['psyche'].profile, req.action)
    except Exception as e:
        print(f"Psych profile update warning: {e}")
    # ------------------------------------------------------
    
    # 0. Hydrate Orchestrator & Director
    from src.narrative_orchestrator import NarrativeOrchestrator
    
    # Load Orchestrator
    orchestrator_data = state['narrative_orchestrator'].orchestrator_data
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
                
    # Process Combat Update BEFORE Analysis if in combat
    # This allows the Director to react to the changing tide of battle
    combat_update = None
    if orchestrator.combat_system and orchestrator.combat_system.combatants:
        combat_update = orchestrator.combat_system.update(
            player_health=state['character'].health if hasattr(state['character'], 'health') else 1.0, 
            profile=state['psyche'].profile
        )
            
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
    
    # Get active NPCs from world state (simple scan for now) + Crew
    active_npcs = [npc['name'] for npc in state['world'].npcs if npc.get('location') == state['world'].current_location]
    
    # Helper: Include crew if we are on the ship/start
    loc_lower = str(state['world'].current_location).lower()
    # Assume crew is accessible in main hub/ship
    if True: # For now, always include crew for testing, or refine logic later
         relationships = state.get('relationships')
         if relationships and hasattr(relationships, 'crew'):
             # If Pydantic model
             for c in relationships.crew.values():
                 # Handle both dict and object types
                 name = c.get('name') if isinstance(c, dict) else c.name
                 if name and name not in active_npcs:
                     active_npcs.append(name)
         elif relationships and isinstance(relationships, dict) and 'crew' in relationships:
             # If dict
             for c in relationships['crew'].values():
                 name = c.get('name') if isinstance(c, dict) else c.name
                 if name and name not in active_npcs:
                     active_npcs.append(name)
    
    # Mystery Status Check
    is_mystery_solved = False
    mystery_state = state.get('mystery')
    if mystery_state:
        if isinstance(mystery_state, dict):
            is_mystery_solved = mystery_state.get('is_revealed', False)
        else:
            is_mystery_solved = getattr(mystery_state, 'is_revealed', False)
    
    # Auto-trigger ending sequence in state
    if is_mystery_solved and not state['narrative'].ending_triggered:
        state['narrative'].ending_triggered = True

    orchestrator_guidance = orchestrator.get_comprehensive_guidance(
        location=state['world'].current_location,
        active_npcs=active_npcs,
        player_action=req.action,
        psych_profile=state['psyche'].profile,
        is_mystery_solved=is_mystery_solved
    )
    
    # Append immediate combat update result if any
    if combat_update:
        if combat_update.get("action") == "attacks":
            orchestrator_guidance += f"\\n\\n[COMBAT EVENT]\\n{combat_update['attacker']} attacks! Threat: {combat_update['threat_level']}"
        elif combat_update.get("action") == "panic":
            orchestrator_guidance += f"\\n\\n[PSYCHE EVENT]\\n{combat_update['description']}"
            
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
        active_npcs=active_npcs,
        cognitive_states=state.get("cognitive_npc_state", {})
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

from src.session_recap import SessionRecapEngine, RecapStyle
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

@app.get("/api/autosave/status/{session_id}")
def get_autosave_status(session_id: str):
    """Check auto-save status for a session."""
    # In this implementation, we check if there's a metadata file for 'autosave'
    from pathlib import Path
    meta_path = Path("saves/autosave_meta.json")
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            import json
            meta = json.load(f)
            return {"last_save": meta.get("save_time")}
    
    return {"last_save": None}


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
# Starforged AI Game Master Server
# Forced reload trigger
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
    if req.session_id not in SESSIONS:
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


# ============================================================================
# CHAPTER PROGRESSION ENDPOINTS
# ============================================================================

# Global progression manager instance
from src.narrative.progression import ProgressionManager

PROGRESSION_MANAGER = None

def get_progression_manager() -> ProgressionManager:
    """Get or create progression manager singleton."""
    global PROGRESSION_MANAGER
    if PROGRESSION_MANAGER is None:
        PROGRESSION_MANAGER = ProgressionManager()
    return PROGRESSION_MANAGER

@app.get("/api/chapter/current")
def get_current_chapter(session_id: str = "default"):
    """Get current chapter metadata and state."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get or initialize progression state from session
    if 'chapter_progression' not in state:
        manager = get_progression_manager()
        state['chapter_progression'] = manager.state.to_dict()
    else:
        # Hydrate manager with saved state
        manager = get_progression_manager()
        from src.narrative.progression import ChapterState
        manager.state = ChapterState.from_dict(state['chapter_progression'])
    
    return manager.get_state()

@app.get("/api/chapter/regions")
def get_chapter_regions(session_id: str = "default"):
    """Get unlocked and locked regions."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    manager = get_progression_manager()
    
    if 'chapter_progression' in state:
        from src.narrative.progression import ChapterState
        manager.state = ChapterState.from_dict(state['chapter_progression'])
    
    current_chapter = manager.get_current_chapter()
    
    # Get all possible regions from all chapters
    all_regions = set()
    for chapter in manager.chapters.values():
        all_regions.update(chapter.regions_unlocked)
    
    unlocked = []
    locked = []
    
    for region in all_regions:
        is_accessible = manager.is_region_accessible(region)
        region_data = {
            'id': region,
            'accessible': is_accessible
        }
        
        if is_accessible:
            unlocked.append(region_data)
        else:
            # Check why it's locked
            if region not in manager.state.unlocked_regions:
                region_data['reason'] = 'Not unlocked in current chapter'
            else:
                # Find soft lock
                for soft_lock in manager.state.active_soft_locks.values():
                    if soft_lock.active and region in soft_lock.affected_regions:
                        region_data['reason'] = soft_lock.description
                        break
            locked.append(region_data)
    
    return {
        'unlocked': unlocked,
        'locked': locked,
        'total': len(all_regions)
    }

@app.get("/api/chapter/soft-locks")
def get_soft_locks(session_id: str = "default"):
    """Get active soft locks (diegetic barriers)."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    manager = get_progression_manager()
    
    if 'chapter_progression' in state:
        from src.narrative.progression import ChapterState
        manager.state = ChapterState.from_dict(state['chapter_progression'])
    
    active_locks = []
    inactive_locks = []
    
    for lock_id, soft_lock in manager.state.active_soft_locks.items():
        lock_data = {
            'id': lock_id,
            'description': soft_lock.description,
            'affected_regions': soft_lock.affected_regions
        }
        
        if soft_lock.active:
            active_locks.append(lock_data)
        else:
            inactive_locks.append(lock_data)
    
    return {
        'active': active_locks,
        'inactive': inactive_locks
    }

class ChapterAdvanceRequest(BaseModel):
    session_id: str = "default"
    next_chapter_id: str

@app.post("/api/chapter/advance")
def advance_chapter(req: ChapterAdvanceRequest):
    """Advance to the next chapter (validates mission completion)."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    manager = get_progression_manager()
    
    if 'chapter_progression' in state:
        from src.narrative.progression import ChapterState
        manager.state = ChapterState.from_dict(state['chapter_progression'])
    
    # Attempt advancement
    result = manager.advance_chapter(req.next_chapter_id)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Cannot advance chapter'))
    
    # Save updated state
    state['chapter_progression'] = manager.state.to_dict()
    
    return result

@app.get("/api/chapter/progress")
def get_chapter_progress(session_id: str = "default"):
    """Get mission completion status for current chapter (synchronized with Quest Graph)."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    from src.quest_api import _get_quest_graph
    graph = _get_quest_graph(session_id)
    
    current_phase_id = graph.state_manager.current_phase
    phase_data = graph.phases.get(current_phase_id)
    
    if not phase_data:
        return {
            'chapter_id': f"chapter_{current_phase_id}",
            'chapter_name': f"Phase {current_phase_id}",
            'critical_missions': [],
            'completed_missions': [],
            'missing_missions': [],
            'is_complete': True,
            'can_advance': True
        }
    
    critical_quests = phase_data.get('critical_quests', [])
    completed_quests = graph.state_manager.get_completed_quests()
    
    completed_missions = [q for q in critical_quests if q in completed_quests]
    missing_missions = [q for q in critical_quests if q not in completed_quests]
    is_complete = len(missing_missions) == 0
    
    return {
        'chapter_id': f"chapter_{current_phase_id}",
        'chapter_name': phase_data.get('name', f"Phase {current_phase_id}"),
        'critical_missions': critical_quests,
        'completed_missions': completed_missions,
        'missing_missions': missing_missions,
        'is_complete': is_complete,
        'can_advance': is_complete
    }

class DebugChapterRequest(BaseModel):
    session_id: str = "default"
    chapter_id: str

@app.post("/api/debug/chapter/set")
def debug_set_chapter(req: DebugChapterRequest):
    """DEBUG: Force-set chapter without validation."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    manager = get_progression_manager()
    
    if 'chapter_progression' in state:
        from src.narrative.progression import ChapterState
        manager.state = ChapterState.from_dict(state['chapter_progression'])
    
    success = manager.force_set_chapter(req.chapter_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Chapter not found: {req.chapter_id}")
    
    # Save updated state
    state['chapter_progression'] = manager.state.to_dict()
    
    return {
        'success': True,
        'chapter': manager.get_state()
    }

class DebugUnlockRegionRequest(BaseModel):
    session_id: str = "default"
    region_id: str

@app.post("/api/debug/chapter/unlock-region")
def debug_unlock_region(req: DebugUnlockRegionRequest):
    """DEBUG: Bypass region locks."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    manager = get_progression_manager()
    
    if 'chapter_progression' in state:
        from src.narrative.progression import ChapterState
        manager.state = ChapterState.from_dict(state['chapter_progression'])
    
    manager.unlock_region(req.region_id)
    
    # Also clear any soft locks affecting this region
    for soft_lock in manager.state.active_soft_locks.values():
        if req.region_id in soft_lock.affected_regions:
            soft_lock.active = False
    
    # Save updated state
    state['chapter_progression'] = manager.state.to_dict()
    
    return {
        'success': True,
        'region_id': req.region_id,
        'accessible': manager.is_region_accessible(req.region_id)
    }

# ============================================================================

def run():
    uvicorn.run("src.server:app", host="0.0.0.0", port=8000, reload=True)

# ============================================================================
# Cognitive Engine Endpoints
# ============================================================================

@app.post("/api/cognitive/interact")
async def cognitive_interact(req: ActionRequest):
    """
    Process a turn with the Cognitive Engine.
    Player Input -> Perception -> Memory -> Agency -> Action (JSON)
    """
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
        
    state = SESSIONS[req.session_id]
    
    # 1. Identify Target NPC
    # Heuristic: Check if action mentions a known NPC name or defaults to 'janus_01'
    target_id = "janus_01" 
    relationships = state.get('relationships', {})
    crew = relationships.get('crew', {}) if isinstance(relationships, dict) else relationships.crew
    
    for npc_id, npc in crew.items():
        name = npc.get('name', '') if isinstance(npc, dict) else npc.name
        if name.lower() in req.action.lower():
            target_id = npc_id
            break
            
    # Check if we have this NPC in cognitive cache (fast access)
    # The authoritative state is now in DB, but we keep a runtime cache for the session
    if "cognitive_npc_state" not in state:
        state["cognitive_npc_state"] = {}
        
    if target_id not in state["cognitive_npc_state"]:
        # Initialize from DB or create new
        # For now, we create a fresh runtime state which retrieves from DB on demand
        from src.npc.schemas import CognitiveState, PersonalityProfile
        
        # Check if they exist in DB (via MemoryStream check usually, but here we just init)
        # We need a profile. ideally loaded from DB entities metadata or standard game state.
        # Fallback to default if not found in game state crew
        role = "Unknown"
        traits = ["Survivor"]
        name = target_id
        
        if target_id in crew:
            c = crew[target_id]
            name = c.get('name', target_id) if isinstance(c, dict) else c.name
            role = c.get('role', 'Unknown') if isinstance(c, dict) else c.role
        
        state["cognitive_npc_state"][target_id] = CognitiveState(
            npc_id=target_id,
            profile=PersonalityProfile(
                name=name,
                role=role,
                narrative_seed=f"{name} is a {role} in the Forge.",
                traits=traits,
                current_mood="Neutral"
            )
        )
        
    npc_state = state["cognitive_npc_state"][target_id]
    
    # 2. Run Engine
    engine = NPCCognitiveEngine()
    
    # Location context
    location = state['world'].current_location
    time = f"{state['world'].current_time}"
    
    output = engine.process_turn(
        state=npc_state,
        player_input=req.action,
        location=location,
        time=time
    )
    
    # 3. Update Narrative Output
    narrative_text = output["narrative"]
    state['narrative'].pending_narrative = narrative_text
    
    # 4. Director Propagation of this interaction (Implicit)
    # The event is already logged in DB by the Engine's memory stream.
    # We might want to trigger a Director "Reaction" here?
    # director = DirectorAgent()
    # director.analyze(...) -> could update global tension based on this interaction
    
    return {
        "narrative": narrative_text,
        "state_updates": output["state_updates"]
    }

@app.get("/api/cognitive/debug/{npc_id}")
async def cognitive_debug(npc_id: str, session_id: str = "default"):
    """
    Inspect the Mind of an NPC (Retrieves from DB + Runtime State).
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
        
    state = SESSIONS[session_id]
    
    # Runtime state
    npc_runtime = None
    if "cognitive_npc_state" in state and npc_id in state["cognitive_npc_state"]:
        npc_runtime = state["cognitive_npc_state"][npc_id]
        
    # DB State (Memories)
    from src.database import get_db
    db = get_db()
    
    # Fetch recent memories directly from DB to verify persistence
    rows = db.query(
        """
        SELECT e.summary, e.importance, e.game_timestamp 
        FROM npc_knowledge k 
        JOIN events e ON k.event_id = e.event_id 
        WHERE k.npc_entity_id = ? 
        ORDER BY k.knowledge_id DESC LIMIT 10
        """, 
        (npc_id,)
    )
    
    db_memories = [dict(r) for r in rows]
    
    return {
        "profile": npc_runtime.profile.dict() if npc_runtime else "Not in active cache",
        "recent_memories_db": db_memories,
        "current_plan": npc_runtime.current_plan.dict() if (npc_runtime and npc_runtime.current_plan) else None
    }

class DirectorEventRequest(BaseModel):
    summary: str
    importance: int = 5
    location_id: Optional[str] = None
    
@app.get("/api/narrative/murder-resolution")
async def get_murder_resolution(session_id: str = "default"):
    """
    Generates the murder resolution mirror dialogue based on the player's character identity.
    Returns the full revelation structure with phases and archetype-specific content.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Import here to avoid circular dependencies
    from src.character_identity import WoundType
    from src.narrative.murder_mirror import MirrorSystem
    
    # Get the player's dominant wound from their psychological profile
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    # Access the wound profile
    wound = WoundType.UNKNOWN
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'identity'):
        wound = psyche.profile.identity.wound_profile.dominant_wound
    elif hasattr(psyche, 'identity'):
        wound = psyche.identity.wound_profile.dominant_wound
    
    # If wound is still unknown, default to CONTROLLER as a safe fallback
    if wound == WoundType.UNKNOWN:
        wound = WoundType.CONTROLLER
        
    revelation = MirrorSystem.generate_revelation(wound)
    
    return {
        "player_wound": wound.value,
        "revelation": revelation
    }

@app.post("/api/director/event")
async def trigger_director_event(req: DirectorEventRequest):
    """
    Manually trigger a global World Event via the Director.
    """
    director = DirectorAgent()
    director.publish_global_event(
        summary=req.summary,
        importance=req.importance,
        location_id=req.location_id
    )
    return {"status": "Event published", "summary": req.summary}


@app.get("/api/narrative/reyes/journal")
def get_reyes_journal(session_id: str = "default", entry_id: Optional[str] = None):
    """
    Retrieve Captain Reyes's journal fragments.
    If entry_id is provided, returns that specific entry.
    Otherwise returns all available entries.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if entry_id:
        entry = ReyesJournalSystem.get_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail=f"Journal entry not found: {entry_id}")
        return entry
    
    return {"entries": ReyesJournalSystem.get_all_entries()}



@app.post("/api/narrative/revelation/choice-crystallized")
def trigger_choice_crystallized(session_id: str = "default"):
    """
    Triggers Stage 4 of the Revelation Ladder.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Safely access wound profile
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
        
    current_wound = WoundType.UNKNOWN
    # Support both structure types depending on how GameState unpacks
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        current_wound = psyche.profile.wound_profile.dominant_wound
    elif hasattr(psyche, 'wound_profile'):
         current_wound = psyche.wound_profile.dominant_wound
    
    if current_wound == WoundType.UNKNOWN:
        current_wound = WoundType.CONTROLLER 

    scene_data = ChoiceCrystallizedSystem.get_scene(current_wound)
    
    return scene_data

class RevelationResponse(BaseModel):
    session_id: str
    scene_id: str
    response_type: str # engaged, deflected, attacked
    wound_type: str 

@app.post("/api/narrative/revelation/respond")
def respond_to_revelation(req: RevelationResponse):
    """
    Handle player response to the revelation.
    """
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
        
    state = SESSIONS[req.session_id]
    psyche = state.get('psyche')
    
    profile = None
    if hasattr(psyche, 'profile'):
        profile = psyche.profile
    
    # Access wound profile safely
    target_profile = None
    if profile and hasattr(profile, 'wound_profile'):
         target_profile = profile.wound_profile
    elif hasattr(psyche, 'wound_profile'):
         target_profile = psyche.wound_profile
         
    if not target_profile:
         raise HTTPException(status_code=500, detail="Could not access wound profile structure")
    
    # Convert string back to Enum
    try:
        w_type = WoundType(req.wound_type)
    except ValueError:
        w_type = WoundType.CONTROLLER
        
    record = ChoiceCrystallizedSystem.process_response(
        target_profile, 
        req.scene_id, 
        req.response_type, 
        w_type
    )
    
    return {"status": "recorded", "record": record.to_dict()}


@app.post("/api/narrative/revelation/mirror-moment")
def trigger_mirror_moment(session_id: str = "default"):
    """
    Triggers Stage 1 of the Revelation Ladder (Mirror Moment).
    Requires 25% story progress.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get story progress (you may need to adjust this based on your progress tracking)
    # For now, using scene count as a proxy
    scene_count = len(state.get('narrative', {}).get('history', []))
    story_progress = min(1.0, scene_count / 40.0)  # Assume ~40 scenes = 100%
    
    # Get player's wound
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    current_wound = WoundType.UNKNOWN
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        current_wound = psyche.profile.wound_profile.dominant_wound
    elif hasattr(psyche, 'wound_profile'):
        current_wound = psyche.wound_profile.dominant_wound
    
    if current_wound == WoundType.UNKNOWN:
        current_wound = WoundType.CONTROLLER
    
    # Get scene
    scene_data = MirrorMomentSystem.get_mirror_scene(current_wound, story_progress)
    
    # If scene was successfully retrieved, record it
    if "error" not in scene_data:
        # Access wound profile
        target_profile = None
        if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
            target_profile = psyche.profile.wound_profile
        elif hasattr(psyche, 'wound_profile'):
            target_profile = psyche.wound_profile
        
        if target_profile:
            MirrorMomentSystem.record_delivery(
                target_profile,
                scene_data['scene_id'],
                current_wound
            )
    
    return scene_data


@app.post("/api/narrative/revelation/cost-revealed")
def trigger_cost_revealed(session_id: str = "default"):
    """
    Triggers Stage 2 of the Revelation Ladder (Cost Revealed).
    Requires 40% story progress.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get story progress
    scene_count = len(state.get('narrative', {}).get('history', []))
    story_progress = min(1.0, scene_count / 40.0)
    
    # Get player's wound
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    current_wound = WoundType.UNKNOWN
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        current_wound = psyche.profile.wound_profile.dominant_wound
    elif hasattr(psyche, 'wound_profile'):
        current_wound = psyche.wound_profile.dominant_wound
    
    if current_wound == WoundType.UNKNOWN:
        current_wound = WoundType.CONTROLLER
    
    # Get scene
    from src.narrative.cost_revealed import CostRevealedSystem
    scene_data = CostRevealedSystem.get_cost_scene(current_wound, story_progress)
    
    # Record if successful
    if "error" not in scene_data:
        target_profile = None
        if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
            target_profile = psyche.profile.wound_profile
        elif hasattr(psyche, 'wound_profile'):
            target_profile = psyche.wound_profile
            
        if target_profile:
            CostRevealedSystem.record_delivery(
                target_profile,
                scene_data['scene_id'],
                current_wound
            )
    
    return scene_data


@app.post("/api/narrative/revelation/origin-glimpsed")
def trigger_origin_glimpsed(session_id: str = "default"):
    """
    Triggers Stage 3 of the Revelation Ladder (Origin Glimpsed).
    Requires 55% story progress.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get story progress
    scene_count = len(state.get('narrative', {}).get('history', []))
    story_progress = min(1.0, scene_count / 40.0)
    
    # Get player's wound
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    current_wound = WoundType.UNKNOWN
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        current_wound = psyche.profile.wound_profile.dominant_wound
    elif hasattr(psyche, 'wound_profile'):
        current_wound = psyche.wound_profile.dominant_wound
    
    if current_wound == WoundType.UNKNOWN:
        current_wound = WoundType.CONTROLLER
    
    # Get scene
    from src.narrative.origin_glimpsed import OriginGlimpsedSystem
    scene_data = OriginGlimpsedSystem.get_origin_scene(current_wound, story_progress)
    
    # Record if successful
    if "error" not in scene_data:
        target_profile = None
        if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
            target_profile = psyche.profile.wound_profile
        elif hasattr(psyche, 'wound_profile'):
            target_profile = psyche.wound_profile
            
        if target_profile:
            OriginGlimpsedSystem.record_delivery(
                target_profile,
                scene_data['scene_id'],
                current_wound
            )
    
    return scene_data


@app.post("/api/narrative/revelation/choice-crystallized")
def trigger_choice_crystallized(session_id: str = "default"):
    """
    Triggers Stage 4 of the Revelation Ladder (Choice Crystallized).
    Requires 70% story progress.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get player's wound
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    current_wound = WoundType.CONTROLLER
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        current_wound = psyche.profile.wound_profile.dominant_wound
    elif hasattr(psyche, 'wound_profile'):
        current_wound = psyche.wound_profile.dominant_wound
        
    # Get scene
    from src.narrative.choice_crystallized import ChoiceCrystallizedSystem
    scene_data = ChoiceCrystallizedSystem.get_scene(current_wound)
    
    return scene_data


class RevelationRespondRequest(BaseModel):
    session_id: str
    stage: str
    scene_id: str
    response_type: str
    wound_type: str


@app.post("/api/narrative/revelation/respond")
def respond_revelation(req: RevelationRespondRequest):
    """
    Processes the player's response to a revelation stage.
    """
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    profile = None
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        profile = psyche.profile.wound_profile
    elif hasattr(psyche, 'wound_profile'):
        profile = psyche.wound_profile
        
    if not profile:
        raise HTTPException(status_code=500, detail="Could not access wound profile")

    # Determine which system to use based on stage
    from src.character_identity import WoundType
    try:
        w_type = WoundType(req.wound_type.lower())
    except ValueError:
        w_type = WoundType.CONTROLLER

    record = None
    if req.stage == "choice_crystallized":
        from src.narrative.choice_crystallized import ChoiceCrystallizedSystem
        record = ChoiceCrystallizedSystem.process_response(
            profile, req.scene_id, req.response_type, w_type
        )
    elif req.stage == "origin_glimpsed":
        from src.narrative.origin_glimpsed import OriginGlimpsedSystem
        record = OriginGlimpsedSystem.process_response(
            profile, req.scene_id, req.response_type, w_type
        )
    elif req.stage == "cost_revealed":
        from src.narrative.cost_revealed import CostRevealedSystem
        record = CostRevealedSystem.process_response(
            profile, req.scene_id, req.response_type, w_type
        )
    elif req.stage == "mirror_moment":
        from src.narrative.mirror_moment import MirrorMomentSystem
        record = MirrorMomentSystem.process_response(
            profile, req.scene_id, req.response_type, w_type
        )
    
    if not record:
        raise HTTPException(status_code=400, detail=f"Unsupported revelation stage: {req.stage}")
        
    # Save session
    return {"success": True, "stage": req.stage, "response": req.response_type}


@app.get("/api/narrative/revelation/status")
def get_revelation_status(session_id: str = "default"):
    """Returns the current status of the Revelation Ladder."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    scene_count = len(state.get('narrative', {}).get('history', []))
    story_progress = min(1.0, scene_count / 40.0)
    
    profile = None
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        profile = psyche.profile.wound_profile
    elif hasattr(psyche, 'wound_profile'):
        profile = psyche.wound_profile
        
    if not profile:
        raise HTTPException(status_code=500, detail="Could not access wound profile")

    from src.narrative.revelation_orchestrator import RevelationOrchestrator
    return RevelationOrchestrator.get_status(profile, story_progress)


@app.get("/api/narrative/revelation/check")
def check_for_revelation(session_id: str = "default"):
    """
    Checks if any new revelation stage should be triggered.
    Returns the scene data or null.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
        
    scene_count = len(state.get('narrative', {}).get('history', []))
    story_progress = min(1.0, scene_count / 40.0)
    
    profile = None
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        profile = psyche.profile.wound_profile
    elif hasattr(psyche, 'wound_profile'):
        profile = psyche.wound_profile
        
    if not profile:
        raise HTTPException(status_code=500, detail="Could not access wound profile")

    from src.narrative.revelation_orchestrator import RevelationOrchestrator
    scene_data = RevelationOrchestrator.get_pending_revelation(profile, story_progress)
    
    if scene_data and "error" not in scene_data:
        stage = scene_data.get("stage")
        if stage in ["mirror_moment", "cost_revealed", "origin_glimpsed", "choice_crystallized"]:
            if stage == "mirror_moment":
                from src.narrative.mirror_moment import MirrorMomentSystem
                MirrorMomentSystem.record_delivery(profile, scene_data['scene_id'], profile.dominant_wound)
            elif stage == "cost_revealed":
                from src.narrative.cost_revealed import CostRevealedSystem
                CostRevealedSystem.record_delivery(profile, scene_data['scene_id'], profile.dominant_wound)
            elif stage == "origin_glimpsed":
                from src.narrative.origin_glimpsed import OriginGlimpsedSystem
                OriginGlimpsedSystem.record_delivery(profile, scene_data['scene_id'], profile.dominant_wound)
            elif stage == "choice_crystallized":
                from src.narrative.choice_crystallized import ChoiceCrystallizedSystem
                ChoiceCrystallizedSystem.record_delivery(profile, scene_data['scene_id'], profile.dominant_wound)
    
    return scene_data


# --- INTERROGATION ENDPOINTS ---

class InterrogateStartRequest(BaseModel):
    session_id: str
    npc_id: str

class InterrogateRespondRequest(BaseModel):
    session_id: str
    choice_id: str

@app.post("/api/narrative/interrogate/start")
def start_interrogation(req: InterrogateStartRequest):
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
        
    state = SESSIONS[req.session_id]
    
    # Initialize Manager if needed
    from src.narrative.interrogation import InterrogationManager
    from src.narrative.interrogation_scenes import get_interrogation_scene
    
    # Access via Pydantic model
    manager = state['narrative'].interrogation_manager
    if not manager:
        manager = InterrogationManager()
        state['narrative'].interrogation_manager = manager
        
    scene_map = {
        "security": "torres", "torres": "torres",
        "pilot": "vasquez", "vasquez": "vasquez", 
        "engineer": "kai", "kai": "kai",
        "medic": "okonkwo", "doctor": "okonkwo", "doc": "okonkwo",
        "ember": "ember",
        "scientist": "yuki", "yuki": "yuki"
    }
    
    scene_name = scene_map.get(req.npc_id.lower(), req.npc_id.lower())
    scene = get_interrogation_scene(scene_name)
    
    if not scene:
        raise HTTPException(status_code=404, detail=f"No interrogation scene for {req.npc_id}")
        
    scene_key = f"{scene_name}_{len(manager.active_state.history) if manager.active_state else 0}"
    manager.register_scene(scene_key, scene)
    
    try:
        # Prepare injection data
        web = state.get('relationships')
        if isinstance(web, dict):
             web = RelationshipWeb.from_dict(web)
             
        psyche = state.get('psyche')
        wound_profile = None
        if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
            wound_profile = psyche.profile.wound_profile
        elif hasattr(psyche, 'wound_profile'):
            wound_profile = psyche.wound_profile
            
        node = manager.start_interrogation(scene_key, relationship_web=web, player_wound_profile=wound_profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "npc_text": node.npc_text,
        "choices": [{"id": c.id, "text": c.text} for c in node.choices],
        "is_complete": node.is_terminal
    }

@app.post("/api/narrative/interrogate/respond")
def respond_interrogation(req: InterrogateRespondRequest):
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
        
    state = SESSIONS[req.session_id]
    manager = state['narrative'].interrogation_manager
    
    if not manager or not manager.active_state:
        raise HTTPException(status_code=400, detail="No active interrogation")
        
    try:
        node = manager.advance(req.choice_id)
        
        # If interrogation complete, apply changes to game state
        if node.is_terminal:
            # 1. Apply Relationship Changes
            try:
                npc_id = manager.active_state.npc_id
                # Direct access to relationships crew dict
                if 'relationships' in state and 'crew' in state['relationships']:
                    crew_dict = state['relationships']['crew']
                    if npc_id in crew_dict:
                        crew_dict[npc_id]['trust'] = max(0.0, min(1.0, 
                            crew_dict[npc_id].get('trust', 0.5) + manager.active_state.trust_delta))
                        crew_dict[npc_id]['suspicion'] = max(0.0, min(1.0, 
                            crew_dict[npc_id].get('suspicion', 0.0) + manager.active_state.suspicion_delta))
            except Exception as e:
                print(f"Warning: Could not update relationships: {e}")
            
            # 2. Apply Wound Profile Changes
            try:
                psyche = state.get('psyche')
                if psyche and hasattr(psyche, 'profile'):
                    wound_profile = psyche.profile.wound_profile if hasattr(psyche.profile, 'wound_profile') else None
                    if wound_profile:
                        manager.apply_signals_to_wound_profile(wound_profile)
            except Exception as e:
                print(f"Warning: Could not update wound profile: {e}")
        
        return {
            "npc_text": node.npc_text,
            "choices": [{"id": c.id, "text": c.text} for c in node.choices],
            "is_complete": node.is_terminal,
            "signals": manager.active_state.signals_accumulated,
            "trust_delta": manager.active_state.trust_delta,
            "suspicion_delta": manager.active_state.suspicion_delta
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Scene Templates API
# ============================================================================

@app.get("/api/narrative/scene-templates/list")
def list_scene_templates():
    """List all available scene template types."""
    from src.narrative.scene_templates import list_scene_types
    return {"scene_types": list_scene_types()}


@app.get("/api/narrative/scene-templates/{scene_type}")
def get_scene_template_details(scene_type: str):
    """Get detailed information about a specific scene template."""
    from src.narrative.scene_templates import get_scene_template, SceneType
    
    try:
        st = SceneType(scene_type)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Scene type '{scene_type}' not found")
    
    template = get_scene_template(st)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "scene_type": template.scene_type.value,
        "name": template.name,
        "purpose": template.purpose,
        "trigger_conditions": template.trigger_conditions,
        "beats": [
            {
                "beat_number": beat.beat_number,
                "beat_name": beat.beat_name,
                "description": beat.description,
                "narrative_text": beat.narrative_text,
                "archetype_variations": {k.value: v for k, v in beat.archetype_variations.items()}
            }
            for beat in template.beats
        ],
        "npc_variations": list(template.npc_variations.keys()),
        "archetype_integration": {k.value: v for k, v in template.archetype_integration.items()}
    }


class GenerateSceneRequest(BaseModel):
    session_id: str
    scene_type: str
    npc_id: Optional[str] = None


@app.post("/api/narrative/scene-templates/generate")
def generate_scene_instance(req: GenerateSceneRequest):
    """
    Generate a scene instance based on current game state.
    
    Accepts:
    - session_id: Current game session
    - scene_type: Type of scene to generate
    - npc_id: Optional specific NPC for NPC-variant scenes
    
    Returns:
    - Fully instantiated scene with dialogue, choices, and consequences
    """
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    
    # Get player's archetype
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    player_wound = WoundType.UNKNOWN
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        player_wound = psyche.profile.wound_profile.dominant_wound
    elif hasattr(psyche, 'wound_profile'):
        player_wound = psyche.wound_profile.dominant_wound
    
    if player_wound == WoundType.UNKNOWN:
        player_wound = WoundType.CONTROLLER
    
    # Get story progress
    scene_count = len(state.get('narrative', {}).get('history', []))
    story_progress = min(1.0, scene_count / 40.0)
    
    # Get relationship score if NPC specified
    relationship_score = 0.0
    if req.npc_id:
        relationships = state.get('relationships', {})
        if isinstance(relationships, dict) and 'crew' in relationships:
            crew = relationships['crew']
            if req.npc_id in crew:
                relationship_score = crew[req.npc_id].get('trust', 0.0)
    
    # Generate scene
    from src.narrative.scene_templates import generate_scene_instance as gen_scene, SceneType
    
    try:
        st = SceneType(req.scene_type)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Scene type '{req.scene_type}' not found")
    
    scene_instance = gen_scene(
        scene_type=st,
        player_archetype=player_wound,
        npc_id=req.npc_id,
        story_progress=story_progress,
        relationship_score=relationship_score
    )
    
    return scene_instance


if __name__ == "__main__":
    run()

# ============================================================================
# Ending System API
# ============================================================================

@app.get("/api/ending/decision-prompt")
def get_ending_decision_prompt(session_id: str = "default"):
    """Get the moral decision prompt for the player's archetype."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get player's dominant wound/archetype
    player_wound = state['psyche'].profile.identity.wound_profile.dominant_wound
    archetype = player_wound.value if hasattr(player_wound, 'value') else str(player_wound)
    
    # Hydrate orchestrator
    from src.narrative_orchestrator import NarrativeOrchestrator
    orchestrator_data = state.get("narrative_orchestrator", {}).get("orchestrator_data", {})
    if orchestrator_data:
        orchestrator = NarrativeOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = NarrativeOrchestrator()
    
    # Get decision prompt
    prompt = orchestrator.ending_system.get_decision_prompt(archetype)
    
    return {
        "archetype": archetype,
        "question": prompt["question"],
        "options": prompt["options"]
    }


class EndingChoiceRequest(BaseModel):
    session_id: str
    choice: str  # "accept" or "reject" or specific option key


@app.post("/api/ending/submit-choice")
def submit_ending_choice(req: EndingChoiceRequest):
    """Process the player's ending choice and determine Hero/Tragedy path."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    
    # Get player's archetype
    player_wound = state['psyche'].profile.identity.wound_profile.dominant_wound
    archetype = player_wound.value if hasattr(player_wound, 'value') else str(player_wound)
    
    # Hydrate orchestrator
    from src.narrative_orchestrator import NarrativeOrchestrator
    from src.narrative.endings import EndingType
    
    orchestrator_data = state.get("narrative_orchestrator", {}).get("orchestrator_data", {})
    if orchestrator_data:
        orchestrator = NarrativeOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = NarrativeOrchestrator()
    
    # Process decision
    ending_type = orchestrator.ending_system.process_decision(archetype, req.choice)
    
    # Update state
    state['narrative'].ending_choice = req.choice
    state['narrative'].ending_type = ending_type.value
    state['narrative'].ending_stage = "decision"
    
    # Save orchestrator state
    state['narrative_orchestrator'].orchestrator_data = orchestrator.to_dict()
    
    return {
        "ending_type": ending_type.value,
        "archetype": archetype,
        "choice": req.choice
    }


@app.get("/api/ending/narrative-beat")
def get_ending_narrative_beat(session_id: str = "default", stage: str = "decision"):
    """Get the narrative text for a specific ending stage."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Validate that ending has been triggered
    if not state['narrative'].ending_type:
        raise HTTPException(status_code=400, detail="Ending not yet triggered")
    
    # Get player's archetype
    player_wound = state['psyche'].profile.identity.wound_profile.dominant_wound
    archetype = player_wound.value if hasattr(player_wound, 'value') else str(player_wound)
    
    # Hydrate orchestrator
    from src.narrative_orchestrator import NarrativeOrchestrator
    from src.narrative.endings import EndingType, EndingStage
    
    orchestrator_data = state.get("narrative_orchestrator", {}).get("orchestrator_data", {})
    if orchestrator_data:
        orchestrator = NarrativeOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = NarrativeOrchestrator()
    
    # Convert string to enum
    ending_type = EndingType(state['narrative'].ending_type)
    ending_stage = EndingStage(stage.lower())
    
    # Get narrative beat
    narrative_text = orchestrator.ending_system.get_narrative_beat(
        archetype, ending_type, ending_stage
    )
    
    # Update stage in state
    state['narrative'].ending_stage = stage
    
    return {
        "stage": stage,
        "ending_type": ending_type.value,
        "archetype": archetype,
        "narrative": narrative_text
    }


# ============================================================================
# Comprehensive Ending Variations API
# ============================================================================

@app.get("/api/narrative/ending/sequence")
def get_ending_sequence(session_id: str = "default"):
    """
    Returns the complete ending sequence for the player's archetype.
    Includes both hero and tragedy paths with all 5 stages.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get player's archetype
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    player_wound = WoundType.UNKNOWN
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'identity'):
        player_wound = psyche.profile.identity.wound_profile.dominant_wound
    elif hasattr(psyche, 'identity'):
        player_wound = psyche.identity.wound_profile.dominant_wound
    
    if player_wound == WoundType.UNKNOWN:
        player_wound = WoundType.CONTROLLER
    
    archetype = player_wound.value if hasattr(player_wound, 'value') else str(player_wound)
    
    # Get orchestrator
    from src.narrative.endings import EndingOrchestrator, EndingType, EndingStage
    orchestrator = EndingOrchestrator()
    
    # Get decision prompt
    decision_prompt = orchestrator.get_decision_prompt(archetype)
    
    # Get all narrative beats for both paths
    hero_path = {
        "decision": orchestrator.get_narrative_beat(archetype, EndingType.HERO, EndingStage.DECISION),
        "test": orchestrator.get_narrative_beat(archetype, EndingType.HERO, EndingStage.TEST),
        "resolution": orchestrator.get_narrative_beat(archetype, EndingType.HERO, EndingStage.RESOLUTION),
        "wisdom": orchestrator.get_narrative_beat(archetype, EndingType.HERO, EndingStage.WISDOM),
        "final_scene": orchestrator.get_narrative_beat(archetype, EndingType.HERO, EndingStage.FINAL_SCENE)
    }
    
    tragedy_path = {
        "decision": orchestrator.get_narrative_beat(archetype, EndingType.TRAGEDY, EndingStage.DECISION),
        "test": orchestrator.get_narrative_beat(archetype, EndingType.TRAGEDY, EndingStage.TEST),
        "resolution": orchestrator.get_narrative_beat(archetype, EndingType.TRAGEDY, EndingStage.RESOLUTION),
        "wisdom": orchestrator.get_narrative_beat(archetype, EndingType.TRAGEDY, EndingStage.WISDOM),
        "final_scene": orchestrator.get_narrative_beat(archetype, EndingType.TRAGEDY, EndingStage.FINAL_SCENE)
    }
    
    return {
        "archetype": archetype,
        "moral_question": decision_prompt["question"],
        "decision_options": decision_prompt["options"],
        "hero_path": hero_path,
        "tragedy_path": tragedy_path
    }


@app.post("/api/narrative/ending/decision")
def process_ending_decision(req: EndingChoiceRequest):
    """
    Processes the player's moral decision and determines the ending path.
    Returns the ending type (hero or tragedy) and the next stage.
    """
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[req.session_id]
    
    # Get player's archetype
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    player_wound = WoundType.UNKNOWN
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'identity'):
        player_wound = psyche.profile.identity.wound_profile.dominant_wound
    elif hasattr(psyche, 'identity'):
        player_wound = psyche.identity.wound_profile.dominant_wound
    
    if player_wound == WoundType.UNKNOWN:
        player_wound = WoundType.CONTROLLER
    
    archetype = player_wound.value if hasattr(player_wound, 'value') else str(player_wound)
    
    # Process decision
    from src.narrative.endings import EndingOrchestrator, EndingType
    orchestrator = EndingOrchestrator()
    ending_type = orchestrator.process_decision(archetype, req.choice)
    
    # Update game state
    if hasattr(state['narrative'], 'ending_choice'):
        state['narrative'].ending_choice = req.choice
    if hasattr(state['narrative'], 'ending_type'):
        state['narrative'].ending_type = ending_type.value
    if hasattr(state['narrative'], 'ending_stage'):
        state['narrative'].ending_stage = "test"  # Next stage after decision
    
    return {
        "ending_type": ending_type.value,
        "archetype": archetype,
        "choice": req.choice,
        "next_stage": "test"
    }


@app.get("/api/narrative/ending/progress")
def get_ending_progress(session_id: str = "default", stage: str = "test"):
    """
    Returns the narrative content for a specific stage of the ending sequence.
    Requires that a decision has already been made.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Validate that ending has been triggered
    ending_type_str = None
    if hasattr(state['narrative'], 'ending_type'):
        ending_type_str = state['narrative'].ending_type
    
    if not ending_type_str:
        raise HTTPException(status_code=400, detail="Ending not yet triggered. Make a decision first.")
    
    # Get player's archetype
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    player_wound = WoundType.UNKNOWN
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'identity'):
        player_wound = psyche.profile.identity.wound_profile.dominant_wound
    elif hasattr(psyche, 'identity'):
        player_wound = psyche.identity.wound_profile.dominant_wound
    
    if player_wound == WoundType.UNKNOWN:
        player_wound = WoundType.CONTROLLER
    
    archetype = player_wound.value if hasattr(player_wound, 'value') else str(player_wound)
    
    # Get narrative beat
    from src.narrative.endings import EndingOrchestrator, EndingType, EndingStage
    orchestrator = EndingOrchestrator()
    
    ending_type = EndingType(ending_type_str)
    ending_stage = EndingStage(stage.lower())
    
    narrative_text = orchestrator.get_narrative_beat(archetype, ending_type, ending_stage)
    
    # Update current stage in state
    if hasattr(state['narrative'], 'ending_stage'):
        state['narrative'].ending_stage = stage
    
    return {
        "stage": stage,
        "ending_type": ending_type.value,
        "archetype": archetype,
        "narrative": narrative_text
    }


# ============================================================================
# Port Arrival Sequence API
# ============================================================================

@app.get("/api/narrative/port-arrival/approach")
def get_port_approach(session_id: str = "default", npc_id: Optional[str] = None):
    """
    Get Day 8 approach scene content.
    
    Args:
        session_id: Game session ID
        npc_id: Optional specific NPC conversation to retrieve
        
    Returns:
        Approach scene content with NPC conversations
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get or create port arrival orchestrator
    from src.narrative.port_arrival_orchestrator import PortArrivalOrchestrator
    
    orchestrator_data = state.get("port_arrival_orchestrator", {})
    if orchestrator_data:
        orchestrator = PortArrivalOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = PortArrivalOrchestrator()
    
    # Get approach scene
    scene = orchestrator.get_approach(npc_id)
    
    # Save orchestrator state
    state["port_arrival_orchestrator"] = orchestrator.to_dict()
    
    return scene


@app.get("/api/narrative/port-arrival/docking")
def get_port_docking(session_id: str = "default"):
    """
    Get docking scenario based on story choices.
    
    Args:
        session_id: Game session ID
        
    Returns:
        Docking scene with authority presence based on story state
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Determine story choices from game state
    # These would be set during the investigation/revelation phases
    story_choices = {
        "murder_reported": state.get("narrative", {}).get("murder_reported", False),
        "yuki_past_revealed": state.get("narrative", {}).get("yuki_past_revealed", False),
        "kai_debts_unresolved": state.get("narrative", {}).get("kai_debts_unresolved", True)
    }
    
    # Get or create port arrival orchestrator
    from src.narrative.port_arrival_orchestrator import PortArrivalOrchestrator
    
    orchestrator_data = state.get("port_arrival_orchestrator", {})
    if orchestrator_data:
        orchestrator = PortArrivalOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = PortArrivalOrchestrator()
    
    # Get docking scene
    scene = orchestrator.get_docking(story_choices)
    
    # Save orchestrator state
    state["port_arrival_orchestrator"] = orchestrator.to_dict()
    
    return scene


@app.get("/api/narrative/port-arrival/dispersal")
def get_port_dispersal(session_id: str = "default", npc_id: Optional[str] = None):
    """
    Get NPC dispersal outcomes based on Hero/Tragedy path.
    
    Args:
        session_id: Game session ID
        npc_id: Optional specific NPC to get dispersal for
        
    Returns:
        NPC dispersal content based on ending type
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get ending type from game state
    ending_type = None
    if hasattr(state.get('narrative'), 'ending_type'):
        ending_type = state['narrative'].ending_type
    
    if not ending_type:
        raise HTTPException(
            status_code=400, 
            detail="Ending decision not yet made. Complete the Hero/Tragedy fork first."
        )
    
    # Get or create port arrival orchestrator
    from src.narrative.port_arrival_orchestrator import PortArrivalOrchestrator
    
    orchestrator_data = state.get("port_arrival_orchestrator", {})
    if orchestrator_data:
        orchestrator = PortArrivalOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = PortArrivalOrchestrator()
    
    # Get dispersal
    dispersal = orchestrator.get_dispersal(ending_type, npc_id)
    
    # Save orchestrator state
    state["port_arrival_orchestrator"] = orchestrator.to_dict()
    
    return dispersal


@app.get("/api/narrative/port-arrival/epilogue")
def get_port_epilogue(session_id: str = "default"):
    """
    Get epilogue for the player's archetype and ending path.
    
    Args:
        session_id: Game session ID
        
    Returns:
        Complete epilogue with setting, reflection, closing image, wisdom, and final question
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get player's archetype
    psyche = state.get('psyche')
    if not psyche:
        raise HTTPException(status_code=400, detail="No psychological profile found")
    
    player_wound = WoundType.UNKNOWN
    if hasattr(psyche, 'profile') and hasattr(psyche.profile, 'identity'):
        player_wound = psyche.profile.identity.wound_profile.dominant_wound
    elif hasattr(psyche, 'identity'):
        player_wound = psyche.identity.wound_profile.dominant_wound
    elif hasattr(psyche, 'profile') and hasattr(psyche.profile, 'wound_profile'):
        player_wound = psyche.profile.wound_profile.dominant_wound
    elif hasattr(psyche, 'wound_profile'):
        player_wound = psyche.wound_profile.dominant_wound
    
    if player_wound == WoundType.UNKNOWN:
        player_wound = WoundType.CONTROLLER
    
    # Get ending type from game state
    ending_type = None
    if hasattr(state.get('narrative'), 'ending_type'):
        ending_type = state['narrative'].ending_type
    
    if not ending_type:
        raise HTTPException(
            status_code=400,
            detail="Ending decision not yet made. Complete the Hero/Tragedy fork first."
        )
    
    # Get or create port arrival orchestrator
    from src.narrative.port_arrival_orchestrator import PortArrivalOrchestrator
    
    orchestrator_data = state.get("port_arrival_orchestrator", {})
    if orchestrator_data:
        orchestrator = PortArrivalOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = PortArrivalOrchestrator()
    
    # Get epilogue
    epilogue = orchestrator.get_epilogue_content(player_wound, ending_type)
    
    # Save orchestrator state
    state["port_arrival_orchestrator"] = orchestrator.to_dict()
    
    return epilogue


@app.get("/api/narrative/port-arrival/status")
def get_port_status(session_id: str = "default"):
    """
    Get current port arrival progress and available scenes.
    
    Args:
        session_id: Game session ID
        
    Returns:
        Status information about port arrival progression
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    
    # Get or create port arrival orchestrator
    from src.narrative.port_arrival_orchestrator import PortArrivalOrchestrator
    
    orchestrator_data = state.get("port_arrival_orchestrator", {})
    if orchestrator_data:
        orchestrator = PortArrivalOrchestrator.from_dict(orchestrator_data)
    else:
        orchestrator = PortArrivalOrchestrator()
    
    return orchestrator.get_status()
