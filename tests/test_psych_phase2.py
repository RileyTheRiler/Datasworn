"""
Verification script for Psychological Systems Phase 2: Trauma & Coping.
"""
import sys
import os
sys.path.append(os.getcwd())

from src.narrative_orchestrator import NarrativeOrchestrator
from src.psychology import AddictionSystem, MoralInjurySystem, SubstanceType, TransgressionType

def test_addiction_system():
    print("\n--- Testing Addiction System ---")
    system = AddictionSystem()
    
    # 1. Use a substance
    relief = system.use_substance(SubstanceType.STIM)
    print(f"Stress Relief from Stim: {relief:.2f}")
    assert relief > 0.0
    
    # 2. Decay Satisfaction
    for _ in range(10):
        system.decay_satisfaction(0.1)
    
    effects = system.get_withdrawal_effects()
    print(f"Withdrawal Effects: {effects}")
    # Severity is 0.15 after one use, which is below 0.3 threshold for effects
    # Let's boost severity manually for the test
    system.addictions[SubstanceType.STIM].severity = 0.5
    system.addictions[SubstanceType.STIM].satisfaction = 0.1
    effects = system.get_withdrawal_effects()
    print(f"Forced Withdrawal Effects: {effects}")
    assert len(effects) > 0
    assert "CRAVING: STIM" in effects[0]
    
    print("Addiction System: PASS")

def test_moral_injury_system():
    print("\n--- Testing Moral Injury System ---")
    system = MoralInjurySystem()
    
    # 1. Record a transgression
    system.record_transgression(TransgressionType.KILLING, "Shot a surrendering pirate.", 0.3)
    print(f"Total Guilt: {system.total_guilt:.2f}")
    assert system.total_guilt == 0.3
    
    # 2. Get Guilt Context
    context = system.get_guilt_context()
    print(f"Guilt Context: {context}")
    assert "MODERATE GUILT" in context or "MILD GUILT" in context
    
    # 3. Process Transgression (Therapy)
    system.process_transgression(0)
    print(f"Guilt after processing: {system.total_guilt:.2f}")
    assert system.total_guilt < 0.3
    
    print("Moral Injury System: PASS")

def test_integration():
    print("\n--- Testing Integration ---")
    orch = NarrativeOrchestrator()
    
    # Setup Addiction
    orch.addiction_system.use_substance(SubstanceType.SEDATIVE)
    orch.addiction_system.addictions[SubstanceType.SEDATIVE].severity = 0.6
    orch.addiction_system.addictions[SubstanceType.SEDATIVE].satisfaction = 0.1
    
    # Setup Guilt
    orch.moral_injury_system.record_transgression(TransgressionType.BETRAYAL, "Sold out a friend.", 0.6)
    
    guidance = orch.get_comprehensive_guidance("The Bar", [])
    print("Guidance Snippet:", guidance[-300:])
    
    assert "CRAVING" in guidance
    assert "GUILT" in guidance
    
    print("Integration: PASS")

if __name__ == "__main__":
    test_addiction_system()
    test_moral_injury_system()
    test_integration()
    print("\nALL PSYCHOLOGY PHASE 2 TESTS PASSED")
