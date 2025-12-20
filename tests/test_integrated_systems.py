"""
Tests for Psychological Combat Integration.
"""

import pytest
import time
from src.combat_orchestrator import CombatOrchestrator, EnemyType
from src.psych_profile import PsychologicalProfile, TraumaScar
from src.memory_system import MemoryPalace

def test_stress_increases_attack_delay():
    orch = CombatOrchestrator()
    enemy = orch.add_combatant("e1", "Enemy", EnemyType.SOLDIER)
    
    # Baseline
    profile = PsychologicalProfile()
    profile.stress_level = 0.0
    
    token = orch.token_manager.issue_token(enemy, profile=profile)
    base_delay = token.delay
    
    # High Stress
    profile.stress_level = 0.9
    token_stressed = orch.token_manager.issue_token(enemy, profile=profile)
    
    assert token_stressed.delay > base_delay

def test_trauma_modifiers():
    orch = CombatOrchestrator()
    enemy = orch.add_combatant("e1", "Enemy", EnemyType.SOLDIER)
    profile = PsychologicalProfile()
    
    # Hyper-Vigilance (Faster reaction/tokens)
    profile.trauma_scars.append(TraumaScar(name="Hyper-Vigilance", description="...", trait_modifier={}))
    token_vigilant = orch.token_manager.issue_token(enemy, profile=profile)
    
    # Survivor's Guilt (Hesitation/Slower)
    profile.trauma_scars = [TraumaScar(name="Survivor's Guilt", description="...", trait_modifier={})]
    token_guilt = orch.token_manager.issue_token(enemy, profile=profile)
    
    assert token_vigilant.delay < token_guilt.delay

def test_panic_mechanic():
    orch = CombatOrchestrator()
    profile = PsychologicalProfile()
    profile.stress_level = 0.9  # High enough to panic
    
    # Force panic random check to succeed by mocking or repeating
    # Since we can't easily mock random inside the class without refactoring or patching,
    # we'll run it enough times to be statistically likely or patch it.
    
    import random
    random.seed(42)  # Deterministic?
    
    panicked = False
    for _ in range(20):
        result = orch.update(profile=profile)
        if result and result.get("action") == "panic":
            panicked = True
            break
            
            break
            
    assert panicked

def test_false_memory_injection():
    palace = MemoryPalace()
    
    frag = palace.inject_false_memory("The 7th Crew Member", "You saw them. You definitely saw them.")
    
    assert frag.is_corrupted
    assert not frag.is_locked
    assert frag.id in palace.fragments
    assert palace.fragments[frag.id].title == "The 7th Crew Member"
