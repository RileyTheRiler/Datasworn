"""
Verification script for Narrative Shaping Layer.
Tests ThematicDirector, SeedPlanter, and DialogueShaper.
"""
import sys
import os
import random
from dataclasses import dataclass, field

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.narrative.archetype_types import ArchetypeProfile
from src.shaping.thematic_director import ThematicDirector
from src.shaping.seed_planter import SeedPlanter
from src.shaping.dialogue_shaper import DialogueShaper
from src.director import DirectorPlan, DirectorState, Pacing, Tone

def verify_shaping():
    print("=== Verifying Narrative Shaping Layer ===\n")
    
    # 1. Setup Logic
    thematic = ThematicDirector()
    planter = SeedPlanter()
    shaper = DialogueShaper()
    
    # 2. Mock Profile: "Controller" (Overcontrolled)
    print("Creating Mock 'Controller' Profile...")
    controller_profile = ArchetypeProfile()
    controller_profile.set_weight("controller", 5.0)
    print(f"Primary Archetype: {controller_profile.primary_archetype}")
    print(f"Confidence: {controller_profile.confidence}")
    print(f"Cluster: {controller_profile.get_cluster('controller')}")
    
    # 3. Test Thematic Director
    print("\n--- Testing Thematic Director ---")
    plan = DirectorPlan(notes_for_narrator="Original notes.")
    plan = thematic.apply_archetype_influence(plan, controller_profile)
    
    print(f"Updated Notes:\n{plan.notes_for_narrator}")
    
    failed = False
    if "THEMATIC INFLUENCE: CONTROLLER" not in plan.notes_for_narrator:
        print("[FAIL] Did not properly inject thematic header")
        failed = True
    if "Psychological Need" not in plan.notes_for_narrator:
        print("[FAIL] Did not inject needs")
        failed = True
    if "Oppressive, rigid" not in plan.notes_for_narrator:
         print("[FAIL] Did not inject overcontrolled atmosphere")
         failed = True
         
    if not failed:
        print("[PASS] Thematic Director applied correctly.")

    # 4. Test Seed Planter
    print("\n--- Testing Seed Planter ---")
    state = DirectorState()
    # Force high probability by mocking random? Or just run in loop
    random.seed(42) # Deterministic
    
    # Run 10 times to ensure a seed is planted
    seeds_planted = False
    for _ in range(10):
        plan = DirectorPlan()
        plan = planter.plant_seeds(plan, controller_profile, state)
        if hasattr(plan, 'notes_for_narrator') and plan.notes_for_narrator and "FORESHADOWING" in plan.notes_for_narrator:
            print(f"Seed Planted: {plan.notes_for_narrator}")
            seeds_planted = True
            break
            
    if seeds_planted and len(state.foreshadowing) > 0:
        print(f"Tracked Seeds: {state.foreshadowing}")
        print("[PASS] Seed Planter works.")
    else:
        print("[FAIL] No seeds plant (might be chance, but unlikely with loop).")

    # 5. Test Dialogue Shaper
    print("\n--- Testing Dialogue Shaper ---")
    plan = DirectorPlan()
    plan = shaper.shape_dialogue(plan, controller_profile)
    print(f"Dialogue Notes: {plan.notes_for_narrator}")
    
    if "DIALOGUE GUIDANCE" in plan.notes_for_narrator and "rigidity" in plan.notes_for_narrator:
        print("[PASS] Dialogue Shaper works for Overcontrolled.")
    else:
        print("[FAIL] Dialogue instructions missing or incorrect.")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify_shaping()
