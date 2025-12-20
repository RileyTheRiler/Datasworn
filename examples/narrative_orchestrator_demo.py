"""
Example: Using the Narrative Orchestrator

This demonstrates how all six narrative systems work together
to create a rich, cohesive story experience.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.narrative_orchestrator import NarrativeOrchestrator, StoryPhase
from src.narrative_memory import PlantType
from src.theme_engine import ThemeCategory
from src.narrative_variety import DocumentType, FlashbackTrigger
from src.narrator import build_narrative_prompt, generate_narrative, NarratorConfig

def demo_narrative_orchestrator():
    """Demonstrate the full narrative system."""
    
    # Initialize orchestrator (this would be in your game state)
    orchestrator = NarrativeOrchestrator()
    
    print("=== SCENE 1: SETUP ===\n")
    
    # Plant narrative elements
    mystery_id = orchestrator.narrative_memory.plant_element(
        PlantType.MYSTERY,
        "The nav system failed at the exact moment we entered the Drift",
        importance=0.9,
        involved_characters=["Navigator Voss"],
    )
    print(f"✓ Planted mystery: {mystery_id}")
    
    # Add a recurring motif
    motif_id = orchestrator.narrative_memory.add_motif(
        "symbol",
        "The viewport - staring into the infinite black",
        variations=["the void beyond the glass", "darkness pressed against the window"],
    )
    print(f"✓ Added motif: {motif_id}")
    
    # Attach to narrator
    build_narrative_prompt._orchestrator = orchestrator
    
    # Generate first scene
    print("\n--- Generating Scene 1 ---")
    config = NarratorConfig(style_profile_name="crichton_clinical")
    
    # Simulate narrative generation (would normally call generate_narrative)
    guidance = orchestrator.get_comprehensive_guidance(
        location="Control Deck",
        active_npcs=["Navigator Voss"],
        player_action="I examine the nav console",
    )
    
    print("\nGuidance provided to narrator:")
    print(guidance[:500] + "..." if len(guidance) > 500 else guidance)
    
    # Simulate processing
    orchestrator.process_generated_narrative(
        "You approach the nav console. The viewport shows only darkness...",
        "Control Deck",
        ["Navigator Voss"]
    )
    orchestrator.advance_scene()
    
    print("\n=== SCENE 5: CALLBACK DUE ===\n")
    
    # Fast forward to scene 5
    for _ in range(4):
        orchestrator.advance_scene()
    
    # Now the mystery should need payoff
    pending = orchestrator.narrative_memory.get_pending_payoffs()
    print(f"Pending payoffs: {len(pending)}")
    if pending:
        print(f"  - {pending[0].description}")
    
    # Motif should recur
    motifs_due = orchestrator.narrative_memory.get_motifs_due()
    print(f"\nMotifs due: {len(motifs_due)}")
    if motifs_due:
        print(f"  - {motifs_due[0].description}")
    
    print("\n=== SCENE 10: VARIETY ===\n")
    
    # Fast forward to scene 10
    for _ in range(5):
        orchestrator.advance_scene()
    
    # Check what variety is suggested
    variety_due = orchestrator.narrative_variety.should_vary_narrative()
    print("Narrative variety suggestions:")
    for variety_type, is_due in variety_due.items():
        if is_due:
            print(f"  ✓ {variety_type}")
    
    # Add a document insert
    doc_id = orchestrator.narrative_variety.add_document(
        DocumentType.SHIP_LOG,
        "Nav System Diagnostic - Entry 47",
        "System failure coincided with anomalous energy signature. Origin: unknown.",
        author="Navigator Voss",
    )
    print(f"\nAdded document: {doc_id}")
    
    print("\n=== TENSION CURVE ANALYSIS ===\n")
    
    # Check tension curve
    if orchestrator.story_graph.tension_curve.tension_history:
        avg_tension = orchestrator.story_graph.tension_curve.get_recent_average()
        print(f"Average tension (recent): {avg_tension:.2f}")
        
        pacing_advice = orchestrator.story_graph.tension_curve.get_pacing_guidance(
            orchestrator.current_scene
        )
        if pacing_advice:
            print(f"Pacing advice: {pacing_advice}")
    
    print("\n=== STORY PHASE ===\n")
    
    phase = StoryPhase.detect_phase(orchestrator.story_graph)
    print(f"Current phase: {phase}")
    print(f"Guidance: {StoryPhase.get_phase_guidance(phase)}")
    
    print("\n=== COMPREHENSIVE GUIDANCE (Scene 10) ===\n")
    
    full_guidance = orchestrator.get_comprehensive_guidance(
        location="Engineering Bay",
        active_npcs=["Navigator Voss", "Chief Engineer Kade"],
        player_action="I confront Voss about the nav failure",
    )
    
    print(full_guidance)
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)


if __name__ == "__main__":
    demo_narrative_orchestrator()
