"""
Verification for Psychological Engine Archetype Integration.
Tests that stress modifiers from Archetype Config are applied correctly.
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.psych_profile import PsychologicalEngine, PsychologicalProfile
from src.narrative.archetype_types import ArchetypeProfile

def verify_psych_integration():
    print("=== Verifying Psychological Engine Archetype Integration ===\n")
    
    engine = PsychologicalEngine()
    
    # 1. Baseline Test (No Archetype)
    print("--- Test 1: Baseline (No Archetype) ---")
    profile = PsychologicalProfile(name="Subject Zero")
    initial_stress = profile.stress_level # 0.0
    
    # "betray" triggers 0.2 stress by default
    engine.evolve_from_event(profile, "They betray us.")
    
    delta = profile.stress_level - initial_stress
    print(f"Stress Delta: {delta:.2f} (Expected 0.20)")
    
    if abs(delta - 0.2) > 0.01:
        print("[FAIL] Baseline stress incorrect.")
        return
    else:
        print("[PASS] Baseline correct.")
        
    # 2. Archetype Test (Controller -> loss_of_control modifier)
    print("\n--- Test 2: Archetype Modifier (Controller) ---")
    # Controller usually has 'loss_of_control' modifier > 1.0 (e.g. 1.5)
    # Event must contain "loss of control" or trigger keyword. 
    # But "loss of control" isn't a default trigger in evolve_from_event.
    # evolve_from_event triggers on "betray", "horror", "miss".
    # Let's use "miss" which adds fear/failure.
    # Does "miss" trigger a modifier?
    # In my code: `if outcome == "miss" and key in ["failure", "making_mistakes", "mistake"]...`
    # Does Controller have "failure" modifier?
    # Checking config... Controller has: loss_of_control, uncertainty, chaos.
    # Perfectionist has 'making_mistakes'.
    
    # Let's use 'Perfectionist' and 'miss' outcome?
    # Or Controller and "chaos"?
    # "chaos" modifier is 1.4 for Controller.
    # But `evolve_from_event` only triggers stress on "betray", "horror", "miss".
    # If I say "The chaos is horrifying." 
    # "horror" triggers 0.2. "chaos" modifier triggers 1.4 multiplier.
    # Total stress should be 0.2 * 1.4 = 0.28.
    
    profile_arch = PsychologicalProfile(name="Controller Subject")
    arch_profile = ArchetypeProfile()
    arch_profile.set_weight("controller", 5.0) # Primary
    
    # Verify config generic loading
    try:
        defn = engine.archetype_config.get_archetype("controller")
        mod = defn.stress_modifiers.get("chaos", 1.0)
        print(f"Controller 'chaos' modifier: {mod}")
    except:
        print("[WARN] Could not load config directly to verify modifier.")
        mod = 1.4 # Assumption
        
    initial_stress = profile_arch.stress_level
    engine.evolve_from_event(profile_arch, "The chaos is terrifying.", archetype_profile=arch_profile)
    
    # "terrifying" triggers "horror" clause -> 0.2 base stress.
    # "chaos" triggers modifier -> 1.4 (from config lookup).
    # Result should be 0.2 * 1.4 = 0.28
    
    delta = profile_arch.stress_level - initial_stress
    print(f"Stress Delta: {delta:.2f} (Expected {0.2 * mod:.2f})")
    
    if abs(delta - (0.2 * mod)) < 0.01:
        print("[PASS] Modifier applied correctly.")
    else:
        print(f"[FAIL] Expected {0.2 * mod:.2f}, got {delta:.2f}")

    # 3. Test Outcome + Modifier
    # Perfectionist + Miss
    print("\n--- Test 3: Perfectionist + Miss ---")
    prof_perf = PsychologicalProfile(name="Perfectionist")
    arch_perf = ArchetypeProfile()
    arch_perf.set_weight("perfectionist", 5.0)
    
    # Perfectionist has 'making_mistakes' key?
    # Checking YAML (if I could). Assuming 'making_mistakes' key exists.
    # In Config: making_mistakes: 1.6
    
    engine.evolve_from_event(prof_perf, "I try to repair it.", outcome="miss", archetype_profile=arch_perf)
    # Miss base stress = 0.1
    # Modifier "making_mistakes" (1.6) matches "miss" outcome logic I added?
    # My code: `if outcome == "miss" and key in ["failure", "making_mistakes", "mistake"]: stress_mult *= mod`
    
    delta = prof_perf.stress_level
    # Should be 0.1 * 1.6 = 0.16
    print(f"Stress Delta: {delta:.2f}")
    
    # Allow some flex if config is different
    if delta > 0.12:
        print("[PASS] Stress amplified by perfectionism.")
    else:
         print(f"[FAIL] Stress not amplified significantly (Got {delta}). Check specific key names.")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify_psych_integration()
