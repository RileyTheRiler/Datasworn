"""
Verification script for Director Agent Integration.
Checks if DirectorAgent correctly applies ThematicDirector, SeedPlanter, and DialogueShaper.
"""
import sys
import os
import time
from dataclasses import dataclass, field
from typing import Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Mock classes to avoid full system spinup if needed, 
# but DirectorAgent imports are hard to mock without patching sys.modules.
# We will use real DirectorAgent but mock the State content.

from src.director import DirectorAgent
from src.narrative.archetype_types import ArchetypeProfile
from src.game_state import PsycheState

def verify_director_integration():
    print("=== Verifying Director Agent Archetype Integration ===\n")
    
    # 1. Initialize Director
    print("Initializing DirectorAgent...")
    try:
        director = DirectorAgent()
    except Exception as e:
        print(f"[FAIL] Failed to initialize DirectorAgent: {e}")
        return

    # 2. Setup Mock World State with Archetype Profile
    print("Setting up mock World State...")
    
    # Create profile
    profile = ArchetypeProfile()
    profile.set_weight("fugitive", 5.0) # Fugitive: Fear of commitment, running away
    
    # Create PsycheState (pydantic model or similar struct)
    # The actual code uses 'world_state['psyche']' which is likely the PsycheState object.
    # DirectorAgent.analyze checks `if hasattr(psyche, 'archetype_profile')`
    
    psyche_state = PsycheState()
    # Manually attach the profile (since it's Any type in the model)
    psyche_state.archetype_profile = profile
    # Also attach profile to .profile field for other engines if needed
    # Wait, PsycheState has .profile which is PsychologicalProfile?
    # No, game_state.py definitions: 
    # class PsycheState(BaseModel):
    #    profile: PsychologicalProfile = ...
    #    archetype_profile: Any = None
    
    # We need a PsychologicalProfile too to avoid crashes in other parts of analyze()
    from src.psych_profile import PsychologicalProfile
    psyche_state.profile = PsychologicalProfile(name="Test Subject")
    
    world_state = {
        "psyche": psyche_state,
        "characters": {},
        "location": {"current": "Deep Space"},
        "crew": {}
    }
    
    session_history = "The crew is drifting in deep space. Engines are cold."
    
    # 3. Run Analysis
    print("Running Director Analysis...")
    # This invokes analyze(), which calls apply_archetype_influence etc.
    # LLM might fail (if no server), caught by try-except.
    
    start_time = time.time()
    plan = director.analyze(world_state, session_history)
    duration = time.time() - start_time
    print(f"Analysis took {duration:.2f}s")
    
    # 4. specific Checks
    print("\n--- Checking DirectorPlan ---")
    print(f"Notes:\n{plan.notes_for_narrator}")
    
    failed = False
    
    # Check Thematic Influence (Fugitive)
    if "THEMATIC INFLUENCE: FUGITIVE" in plan.notes_for_narrator:
        print("[PASS] Thematic influence detected.")
    else:
        print("[FAIL] Thematic influence MISSING.")
        failed = True
        
    # Check Seed Planting (Probability manipulated in loop?)
    # DirectorAgent uses `self.seed_planter`. 
    # Logic: 30% + confidence*0.4. Confidence of 5.0 weight separation is high (~1.0). So ~70% chance.
    # We can't guarantee it in one run.
    # But if we see "FORESHADOWING", it works.
    if "FORESHADOWING" in plan.notes_for_narrator:
        print("[PASS] Foreshadowing seed detected (Lucky!).")
    else:
        print("[INFO] No seed planted (Chance event).")
        
    # Check Dialogue Guidance
    # Fugitive is UNDERCONTROLLED
    if "DIALOGUE GUIDANCE" in plan.notes_for_narrator and "volatility" in plan.notes_for_narrator:
        print("[PASS] Dialogue guidance detected.")
    else:
        # Check specific text from DialogueShaper
        # Undercontrolled: "NPCs should react to the player's volatility..."
        if "react to the player's volatility" in plan.notes_for_narrator:
             print("[PASS] Dialogue guidance text found.")
        else:
            print("[FAIL] Dialogue guidance MISSING.")
            failed = True
            
    if not failed:
        print("\n[SUCCESS] Integration Verified.")
    else:
        print("\n[FAILURE] Integration Issues Detected.")

if __name__ == "__main__":
    verify_director_integration()
