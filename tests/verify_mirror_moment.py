"""
Verification script for Mirror Moment (Stage 1) implementation.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.narrative.mirror_moment import MirrorMomentSystem, MIRROR_SCENES
from src.character_identity import WoundType, WoundProfile

def test_all_archetype_scenes():
    print("\n--- Testing All Archetype Mirror Scenes ---")
    
    test_archetypes = [
        WoundType.CONTROLLER,
        WoundType.JUDGE,
        WoundType.GHOST,
        WoundType.FUGITIVE,
        WoundType.CYNIC,
        WoundType.SAVIOR
    ]
    
    for wound in test_archetypes:
        scene = MirrorMomentSystem.get_mirror_scene(wound, story_progress=0.30)
        
        print(f"\n{wound.value.upper()}:")
        print(f"  Mirror Character: {scene['mirror_character']}")
        print(f"  Discovery Type: {scene['discovery_type']}")
        print(f"  Content Length: {len(scene['content'])} chars")
        print(f"  Seed Planted: {scene['seed_planted'][:50]}...")
        
        # Assertions
        assert scene['stage'] == "mirror_moment"
        assert scene['mirror_character'] in ["Captain Reyes", "Torres", "Dr. Okonkwo", "Vasquez"]
        assert scene['discovery_type'] in ["log", "witnessed_scene", "conversation"]
        assert len(scene['content']) > 100
        assert len(scene['seed_planted']) > 20
    
    print("\n✅ All archetype scenes verified")

def test_progress_gating():
    print("\n--- Testing Progress Gating ---")
    
    # Should fail with insufficient progress
    scene_early = MirrorMomentSystem.get_mirror_scene(
        WoundType.CONTROLLER, 
        story_progress=0.10
    )
    
    print(f"Early access (10%): {scene_early.get('error', 'NO ERROR')}")
    assert "error" in scene_early
    assert scene_early['required_progress'] == 0.25
    
    # Should succeed with sufficient progress
    scene_ready = MirrorMomentSystem.get_mirror_scene(
        WoundType.CONTROLLER,
        story_progress=0.30
    )
    
    print(f"Ready access (30%): Success = {'error' not in scene_ready}")
    assert "error" not in scene_ready
    
    print("✅ Progress gating verified")

def test_delivery_recording():
    print("\n--- Testing Delivery Recording ---")
    
    profile = WoundProfile(
        dominant_wound=WoundType.GHOST,
        revelation_progress=0.0
    )
    
    print(f"Initial progress: {profile.revelation_progress}")
    print(f"Initial history: {len(profile.revelation_history)}")
    
    record = MirrorMomentSystem.record_delivery(
        profile,
        "test-scene-456",
        WoundType.GHOST
    )
    
    print(f"After delivery progress: {profile.revelation_progress}")
    print(f"After delivery history: {len(profile.revelation_history)}")
    
    assert profile.revelation_progress == 0.25
    assert len(profile.revelation_history) == 1
    assert profile.revelation_history[0].stage == "mirror_moment"
    assert profile.revelation_history[0].player_response == "observed"
    
    print("✅ Delivery recording verified")

def test_fallback_behavior():
    print("\n--- Testing Fallback Behavior ---")
    
    # Unknown wound should fallback to Controller
    scene = MirrorMomentSystem.get_mirror_scene(
        WoundType.UNKNOWN,
        story_progress=0.30
    )
    
    print(f"Unknown wound fallback: {scene['mirror_character']}")
    assert scene['mirror_character'] == "Captain Reyes"  # Controller's mirror
    
    print("✅ Fallback behavior verified")

if __name__ == "__main__":
    try:
        test_all_archetype_scenes()
        test_progress_gating()
        test_delivery_recording()
        test_fallback_behavior()
        print("\n🎉 ALL MIRROR MOMENT TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
