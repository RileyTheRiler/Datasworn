"""
Verification script for Archetype Foreshadowing System.
Simulates player progression and archetype emergence to verify seed selection.
"""

from src.narrative.foreshadowing import ForeshadowingEngine, SeedType, GamePhase
from src.character_identity import WoundType

def test_foreshadowing():
    engine = ForeshadowingEngine()
    
    print("--- TEST 1: AMBIENT PHASE (CONTROLLER) ---")
    scores = {WoundType.CONTROLLER: 0.5}
    progress = 0.1
    seeds = engine.select_seeds(scores, progress, location="Bridge", npc="Torres")
    print(f"Phase: {engine.get_phase_from_progress(progress)}")
    print(engine.get_narrator_instructions(seeds))
    
    print("\n--- TEST 2: TARGETED PHASE (JUDGE) ---")
    scores = {WoundType.JUDGE: 0.6}
    progress = 0.4
    seeds = engine.select_seeds(scores, progress, location="Captain's Quarters", npc="Vasquez")
    print(f"Phase: {engine.get_phase_from_progress(progress)}")
    print(engine.get_narrator_instructions(seeds))
    
    print("\n--- TEST 3: CONVERGENCE PHASE (GHOST) ---")
    scores = {WoundType.GHOST: 0.8}
    progress = 0.7
    seeds = engine.select_seeds(scores, progress, location="Cargo Bay", npc="Kai")
    print(f"Phase: {engine.get_phase_from_progress(progress)}")
    print(engine.get_narrator_instructions(seeds))
    
    print("\n--- TEST 4: SYMBOLIC SEEDS ONLY ---")
    scores = {WoundType.FUGITIVE: 0.7}
    progress = 0.5
    # No location or NPC, should only pick symbolic or context-less seeds
    seeds = engine.select_seeds(scores, progress)
    print(f"Phase: {engine.get_phase_from_progress(progress)}")
    print(engine.get_narrator_instructions(seeds))

if __name__ == "__main__":
    test_foreshadowing()
