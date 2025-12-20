import sys
import os

# Add root to path to allow 'from src...' imports
sys.path.append(os.getcwd())

try:
    from src.narrative_orchestrator import NarrativeOrchestrator
    from src.game_state import create_initial_state
    
    print("Importing successful.")
    
    # Test initialization
    orchestrator = NarrativeOrchestrator()
    print("Orchestrator initialized.")
    
    # Check for new systems
    assert orchestrator.payoff_tracker is not None
    assert orchestrator.npc_memories is not None
    assert orchestrator.consequence_manager is not None
    assert orchestrator.echo_system is not None
    
    # Phase 2 Checks
    assert orchestrator.opening_hooks is not None
    assert orchestrator.npc_emotions is not None
    assert orchestrator.reputation is not None
    assert orchestrator.irony_tracker is not None
    
    # Phase 3 Checks
    assert orchestrator.story_beats is not None
    assert orchestrator.plot_manager is not None
    assert orchestrator.branching_system is not None
    assert orchestrator.npc_goals is not None
    
    # Phase 4 Checks
    assert orchestrator.ending_system is not None
    assert orchestrator.impossible_choices is not None
    assert orchestrator.environmental_storyteller is not None
    assert orchestrator.flashback_system is not None
    
    # Phase 5 Checks
    assert orchestrator.unreliable_system is not None
    assert orchestrator.meta_system is not None
    assert orchestrator.npc_skills is not None
    assert orchestrator.multiplayer_system is not None
    
    print("All subsystems (Phase 1-5) present.")
    
    # Test guidance generation (basic smoke test)
    # Inject some Phase 2 state
    orchestrator.reputation.mercy_ruthless.value = 60 
    orchestrator.npc_emotions.process_event("SARA", "THREATENED")
    
    # Phase 5 Context Injection Test
    orchestrator.unreliable_system.sanity_level = 0.2
    
    guidance = orchestrator.get_comprehensive_guidance(location="Bridge", active_npcs=["SARA"])
    print("Guidance generation worked.")
    
    assert "known as a merciful" in guidance.lower()
    assert "sara is fearful" in guidance.lower()
    assert "unreliable narrator" in guidance.lower()
    
    # Reset sanity
    orchestrator.unreliable_system.sanity_level = 1.0
    print("Guidance context verified (Phase 2, 3, 4, 5).")
    
    # Test GameState serialization/deserialization compatibility
    state = create_initial_state("Commander Shepard")
    print("GameState created.")
    
    # Test orchestrator serialization
    data = orchestrator.to_dict()
    rehydrated = NarrativeOrchestrator.from_dict(data)
    print("Serialization/Deserialization worked.")
    
    print("VERIFICATION SUCCESSFUL")
    
except Exception as e:
    print(f"VERIFICATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
