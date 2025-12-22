"""
Verification script for Origin Glimpsed (Stage 3) implementation.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.narrative.origin_glimpsed import OriginGlimpsedSystem, ORIGIN_SCENES
from src.character_identity import WoundType, WoundProfile

def test_all_archetype_scenes():
    print("\n--- Testing All Archetype Origin Scenes ---")
    
    test_archetypes = [
        WoundType.CONTROLLER,
        WoundType.JUDGE,
        WoundType.GHOST,
        WoundType.FUGITIVE,
        WoundType.CYNIC,
        WoundType.SAVIOR
    ]
    
    for wound in test_archetypes:
        scene = OriginGlimpsedSystem.get_origin_scene(wound, story_progress=0.60)
        
        print(f"\n{wound.value.upper()}:")
        print(f"  Event: {scene['trigger_event'][:50]}...")
        print(f"  Insight: {scene['insight']}")
        
        # Assertions
        assert scene['stage'] == "origin_glimpsed"
        assert len(scene['revelation']) > 50
    
    print("\n✅ All archetype scenes verified")

def test_progress_gating():
    print("\n--- Testing Progress Gating ---")
    
    # Should fail with insufficient progress (< 55%)
    scene_early = OriginGlimpsedSystem.get_origin_scene(
        WoundType.CONTROLLER, 
        story_progress=0.50
    )
    
    print(f"Early access (50%): {scene_early.get('error', 'NO ERROR')}")
    assert "error" in scene_early
    assert scene_early['required_progress'] == 0.55
    
    # Should succeed with sufficient progress
    scene_ready = OriginGlimpsedSystem.get_origin_scene(
        WoundType.CONTROLLER,
        story_progress=0.56
    )
    
    print(f"Ready access (56%): Success = {'error' not in scene_ready}")
    assert "error" not in scene_ready
    
    print("✅ Progress gating verified")

def test_delivery_recording():
    print("\n--- Testing Delivery Recording ---")
    
    profile = WoundProfile(
        dominant_wound=WoundType.SAVIOR,
        revelation_progress=0.40
    )
    
    record = OriginGlimpsedSystem.record_delivery(
        profile,
        "test-scene-origin-999",
        WoundType.SAVIOR
    )
    
    print(f"Progress updated to: {profile.revelation_progress}")
    
    assert profile.revelation_progress == 0.55
    assert len(profile.revelation_history) == 1
    assert profile.revelation_history[0].stage == "origin_glimpsed"
    
    print("✅ Delivery recording verified")

if __name__ == "__main__":
    try:
        test_all_archetype_scenes()
        test_progress_gating()
        test_delivery_recording()
        print("\n🎉 ALL ORIGIN GLIMPSED TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)
