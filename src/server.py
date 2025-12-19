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

class InitRequest(BaseModel):
    character_name: str
    background_vow: str

class ActionRequest(BaseModel):
    session_id: str
    action: str

@app.get("/")
def health_check():
    return {"status": "online", "system": "Starforged AI GM"}

@app.post("/api/session/start")
def start_session(req: InitRequest):
    session_id = "default"  # Single session for MVP
    state = create_initial_state(req.character_name)
    
    # Generate initial assets
    # Background portrait generation (could be async in real app)
    # Background portrait generation (could be async in real app)
    # Wrap in try/except to prevent crash, though image_gen already handles it.
    try:
        portrait_url = generate_portrait(req.character_name, "A gritty female sci-fi survivor, determined expression")
    except Exception:
        portrait_url = None
    
    if not portrait_url:
        portrait_url = "/assets/defaults/portrait_placeholder.png"
    
    # Store in state (assuming we might add visual fields to state later, 
    # for now just returning them or we can extend GameState dynamically/wrapper)
    
    SESSIONS[session_id] = state
    
    # Initial Narrative
    intro_narrative = generate_narrative(
        player_input="[Begin Game]",
        character_name=req.character_name,
        location="The Forge",
        context="The game begins. You are a female spacer in the Forge.",
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
    
    # 1. Generate Narrative
    narrative = generate_narrative(
        player_input=req.action,
        character_name=state['character'].name,
        location=state['world'].current_location,
        context=state['narrative'].pending_narrative, # Use previous as context
        config=NarratorConfig(backend="gemini")
    )
    
    # Update State
    state['narrative'].pending_narrative = narrative
    
    # 2. Check for Location Change / Generate Visuals
    # We generate an image for the current moment to visualize the narrative
    image_prompt = f"{state['world'].current_location}. {narrative[:100]}..."
    image_url = None
    try:
        # Generate with a filename based on session and turn to avoid collisions/caching issues
        # (Mocking turn count with hash of narrative for now)
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
    
    narrative = generate_narrative(
        player_input=action_desc,
        roll_result=str(roll_result),
        outcome=outcome_key,
        character_name=state['character'].name,
        location=state['world'].current_location,
        context=state['narrative'].pending_narrative,
        config=NarratorConfig(backend="gemini")
    )
    
    # Update state history/pending narrative
    state['narrative'].pending_narrative = narrative
    
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


def run():
    uvicorn.run("src.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
