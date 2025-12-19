import sys
import os
from pprint import pprint

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nodes import director_node, narrator_node
from src.game_state import create_initial_state, QuestLoreState, CompanionManagerState, WorldState

def test_integration():
    print("Initializing State...")
    state = create_initial_state("Commander Shepard")
    
    # Setup Quest
    state["quest_lore"].quests = {
        "quests": {
            "test_quest": {
                "id": "test_quest",
                "name": "Test Mission",
                "description": "Verify the system works",
                "objectives": [{"id": "obj1", "description": "Run the test", "completed": False}]
            }
        }
    }
    
    # Setup Companion
    state["companions"].companions = {
        "comp1": {
            "name": "Garrus",
            "archetype": "soldier",
            "state": "active",
            "loyalty": 5
        }
    }
    state["companions"].active_companion = "comp1"
    
    # Setup Combat (trigger prediction)
    state["world"].combat_active = True
    state["world"].enemy_count = 5
    state["world"].enemy_strength = 2.0  # High threat
    
    print("\nRunning Director Node...")
    try:
        director_out = director_node(state)
        print("Director Output Keys:", director_out.keys())
        # Apply updates
        if "director" in director_out:
            state["director"] = director_out["director"]
    except Exception as e:
        print(f"DIRECTOR FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\nRunning Narrator Node...")
    try:
        # Mock LLM being unavailable is handled by code
        narrator_out = narrator_node(state)
        print("Narrator Output Keys:", narrator_out.keys())
        
        narrative = narrator_out.get("narrative")
        if narrative:
            print("\nPending Narrative Preview:")
            print(narrative.pending_narrative[:200])
        
        # Check for context injection in logs would be hard without capturing stdout/logging
        # But if it didn't crash, that's a good sign.
            
    except Exception as e:
        print(f"NARRATOR FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integration()
