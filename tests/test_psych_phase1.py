"""
Verification script for Psychological Systems Phase 1: Core Psyche.
"""
import sys
import os
sys.path.append(os.getcwd())

from src.narrative_orchestrator import NarrativeOrchestrator
from src.psychology import DreamSequenceEngine, PhobiaSystem
import random

def test_dream_engine():
    print("\n--- Testing Dream Engine ---")
    random.seed(42)  # Ensure deterministic output
    engine = DreamSequenceEngine()
    
    # 1. Normal Dream
    dream = engine.generate_dream(
        recent_memories=["Found a derelict ship", "Fixed the engine"],
        suppressed_memories=[],
        dominant_emotion="curious",
        stress_level=0.1
    )
    print(f"Normal Dream: {dream}")
    assert "Found a derelict ship" in dream or "Fixed the engine" in dream
    
    # 2. Nightmare
    nightmare = engine.generate_dream(
        recent_memories=[],
        suppressed_memories=["The airlock failure"],
        dominant_emotion="afraid",
        stress_level=0.9
    )
    print(f"Nightmare: {nightmare}")
    assert "breathing water" in nightmare
    assert "chasing you" in nightmare
    assert "airlock failure" in nightmare
    
    print("Dream Engine: PASS")

def test_phobia_system():
    print("\n--- Testing Phobia System ---")
    system = PhobiaSystem()
    
    # Add Arachnophobia
    system.add_phobia("Arachnophobia", ["spider", "webs", "skittering"], severity=0.8)
    
    # 1. Safe Text
    panic = system.check_triggers("The room is clean and bright.")
    assert panic == 0.0
    
    # 2. Triggered Text
    panic_inc = system.check_triggers("You hear skittering in the vents.")
    print(f"Panic Increase: {panic_inc}")
    assert panic_inc > 0.1
    
    # 3. Panic Attack
    # Force panic
    system.active_phobias["Arachnophobia"].accumulated_panic = 1.0
    status = system.get_panic_status()
    print(f"Status: {status}")
    assert "PANIC ATTACK: Arachnophobia" in status
    
    print("Phobia System: PASS")

def test_integration():
    print("\n--- Testing Integration ---")
    orch = NarrativeOrchestrator()
    
    # Setup Phobia
    orch.phobia_system.add_phobia("Darkness", ["shadow", "dark", "pitch black"], severity=1.0)
    
    # Trigger it
    orch.phobia_system.check_triggers("It is pitch black in here.")
    orch.phobia_system.check_triggers("The shadows are moving.")
    orch.phobia_system.check_triggers("Darkness consumes all.")
    # Force full panic manually just in case check_triggers accumulation varies
    orch.phobia_system.active_phobias["Darkness"].accumulated_panic = 1.5
    
    guidance = orch.get_comprehensive_guidance("Dark Room", [])
    print("Guidance Snippet:", guidance[-200:])
    
    assert "PANIC ATTACK: Darkness" in guidance
    
    print("Integration: PASS")

if __name__ == "__main__":
    test_dream_engine()
    test_phobia_system()
    test_integration()
    print("\nALL PSYCHOLOGY PHASE 1 TESTS PASSED")
