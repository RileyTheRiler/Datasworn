"""
Verification script for Interrogation System using the new engine components.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.narrative.interrogation import InterrogationManager, InterrogationSignal
from src.narrative.interrogation_scenes import get_interrogation_scene

def test_interrogation_flow():
    print(">>> Initializing Interrogation Manager...")
    manager = InterrogationManager()
    
    # Register Torres Scene
    print(">>> Registering Torres Scene...")
    torres_scene = get_interrogation_scene("torres")
    manager.register_scene("torres_intro", torres_scene)
    
    # Start Interrogation
    print(">>> Starting Interrogation with Torres...")
    node = manager.start_interrogation("torres_intro")
    print(f"NPC: {node.npc_text}")
    print(f"Choices: {[c.text[:20] + '...' for c in node.choices]}")
    
    assert len(node.choices) > 0, "No choices found for Torres start node"
    
    # Make a Choice (Demanding - Option 0)
    choice = node.choices[0] # Demanding
    print(f"\n>>> Selected Choice: {choice.text}")
    print(f"Expected Signals: {choice.signals}")
    
    next_node = manager.advance(choice.id)
    print(f"NPC Response: {next_node.npc_text}")
    
    # Verify Signals
    state = manager.active_state
    print(f"Accumulated Signals: {state.signals_accumulated}")
    
    assert state.signals_accumulated.get(InterrogationSignal.CONTROLLER.value) == 1, "Controller signal not tracked!"
    assert next_node.is_terminal, "Expected terminal node (shut_down)"
    
    print("\n[SUCCESS] Basic Flow Verified.")

def test_yuki_flow():
    print("\n>>> Testing Yuki Confrontation...")
    manager = InterrogationManager()
    yuki_scene = get_interrogation_scene("yuki")
    manager.register_scene("yuki_final", yuki_scene)
    
    node = manager.start_interrogation("yuki_final")
    
    # 1. Confront
    choice = node.choices[0] # Moral confrontation
    node = manager.advance(choice.id)
    
    print(f"NPC: {node.npc_text}")
    assert "Yes. I killed him" in node.npc_text, "Confession not triggered"
    
    # 2. Decision
    choice = node.choices[1] # Tragedy
    node = manager.advance(choice.id)
    
    state = manager.active_state
    assert state.signals_accumulated.get(InterrogationSignal.GHOST.value) == 1, "Ghost signal not tracked"
    print("\n[SUCCESS] Yuki Flow Verified.")

if __name__ == "__main__":
    try:
        test_interrogation_flow()
        test_yuki_flow()
        print("\nAll Interrogation tests passed!")
    except Exception as e:
        print(f"\n[FAILED] {e}")
        import traceback
        traceback.print_exc()
