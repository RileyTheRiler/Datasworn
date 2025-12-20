"""
Verification script for Psychological Systems Phase 3: Social Psyche.
"""
import sys
import os
sys.path.append(os.getcwd())

from src.narrative_orchestrator import NarrativeOrchestrator
from src.psychology import AttachmentSystem, AttachmentStyle, TrustDynamicsSystem, BetrayalSeverity

def test_attachment_system():
    print("\n--- Testing Attachment System ---")
    system = AttachmentSystem()
    system.style = AttachmentStyle.ANXIOUS
    
    # Positive interaction
    system.process_positive_interaction("KIRA")
    rel = system.relationships["KIRA"]
    print(f"After positive: Trust={rel.trust:.2f}, Closeness={rel.closeness:.2f}")
    assert rel.closeness > 0.5  # Anxious clings fast
    
    # Conflict
    system.process_conflict("KIRA")
    print(f"After conflict: Trust={rel.trust:.2f}, Closeness={rel.closeness:.2f}")
    assert rel.trust < 0.5  # Anxious loses trust fast
    
    # Guidance
    rel.closeness = 0.2
    guidance = system.get_relationship_guidance("KIRA")
    print(f"Guidance: {guidance}")
    assert "Anxious" in guidance
    
    print("Attachment System: PASS")

def test_trust_dynamics():
    print("\n--- Testing Trust Dynamics ---")
    system = TrustDynamicsSystem()
    
    # Record Betrayal
    system.record_betrayal("MARCUS", "Sold our coordinates to the enemy.", BetrayalSeverity.MAJOR)
    print(f"Trust after betrayal: {system.get_trust('MARCUS'):.2f}")
    assert system.get_trust("MARCUS") < 0.3
    
    # Context
    context = system.get_trust_context("MARCUS")
    print(f"Context: {context}")
    assert "Broken" in context
    
    # Forgiveness
    system.forgive_betrayal(0)
    print(f"Trust after forgiveness: {system.get_trust('MARCUS'):.2f}")
    assert system.get_trust("MARCUS") > 0.0  # Some restoration occurred
    
    print("Trust Dynamics: PASS")

def test_integration():
    print("\n--- Testing Integration ---")
    orch = NarrativeOrchestrator()
    
    # Setup Attachment
    orch.attachment_system.style = AttachmentStyle.AVOIDANT
    orch.attachment_system.process_positive_interaction("ZARA")
    orch.attachment_system.process_positive_interaction("ZARA")
    orch.attachment_system.process_positive_interaction("ZARA")
    orch.attachment_system.process_positive_interaction("ZARA")
    orch.attachment_system.relationships["ZARA"].closeness = 0.8
    
    # Setup Trust
    orch.trust_dynamics.record_betrayal("ZARA", "Lied about the cargo.", BetrayalSeverity.MODERATE)
    
    guidance = orch.get_comprehensive_guidance("Ship Bridge", ["ZARA"])
    print("Guidance Snippet:", guidance[-400:])
    
    assert "Avoidant" in guidance or "TRUST" in guidance.upper()
    
    print("Integration: PASS")

if __name__ == "__main__":
    test_attachment_system()
    test_trust_dynamics()
    test_integration()
    print("\nALL PSYCHOLOGY PHASE 3 TESTS PASSED")
