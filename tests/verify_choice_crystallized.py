
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.narrative.choice_crystallized import ChoiceCrystallizedSystem, SCENE_DATA
from src.character_identity import WoundType, WoundProfile, IdentityArchetype, IdentityScore
from src.psychology_api_models import *

def test_scene_content():
    print("\n--- Testing Scene Content Retrieval ---")
    
    # Test Controller (explicit)
    scene = ChoiceCrystallizedSystem.get_scene(WoundType.CONTROLLER)
    print(f"Controller Scene Pattern: {scene['pattern_name']}")
    assert scene['pattern_name'] == "The Controller"
    assert "You never stop, do you?" in scene['dialogue']
    
    # Test Fallback (Unknown -> Controller)
    scene_fallback = ChoiceCrystallizedSystem.get_scene(WoundType.UNKNOWN)
    print(f"Unknown (Fallback) Scene Pattern: {scene_fallback['pattern_name']}")
    assert scene_fallback['pattern_name'] == "The Controller"
    
    # Test Another Archetype
    scene_ghost = ChoiceCrystallizedSystem.get_scene(WoundType.GHOST)
    print(f"Ghost Scene Pattern: {scene_ghost['pattern_name']}")
    assert scene_ghost['pattern_name'] == "The Ghost"
    
    print("✅ Scene content retrieval verified.")

def test_response_recording():
    print("\n--- Testing Response Recording ---")
    
    # Setup specific wound profile
    profile = WoundProfile(
        dominant_wound=WoundType.JUDGE,
        revelation_progress=0.4
    )
    
    scene_id = "test-scene-123"
    response_type = "engaged"
    
    print(f"Initial Progress: {profile.revelation_progress}")
    print(f"Initial History: {len(profile.revelation_history)}")
    
    record = ChoiceCrystallizedSystem.process_response(
        profile,
        scene_id,
        response_type,
        WoundType.JUDGE
    )
    
    print(f"New Progress: {profile.revelation_progress}")
    print(f"New History: {len(profile.revelation_history)}")
    
    assert profile.revelation_progress == 0.75
    assert len(profile.revelation_history) == 1
    assert profile.revelation_history[0].player_response == "engaged"
    assert profile.revelation_history[0].archetype_at_delivery == "judge"
    
    print("✅ Response recording verified.")

if __name__ == "__main__":
    try:
        test_scene_content()
        test_response_recording()
        print("\n🎉 ALL TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)
