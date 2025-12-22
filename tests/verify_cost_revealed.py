"""
Verification script for Cost Revealed (Stage 2) implementation.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.narrative.cost_revealed import CostRevealedSystem, COST_SCENES
from src.character_identity import WoundType, WoundProfile

def test_all_archetype_scenes():
    print("\n--- Testing All Archetype Cost Scenes ---")
    
    test_archetypes = [
        WoundType.CONTROLLER,
        WoundType.JUDGE,
        WoundType.GHOST,
        WoundType.FUGITIVE,
        WoundType.CYNIC,
        WoundType.SAVIOR
    ]
    
    for wound in test_archetypes:
        scene = CostRevealedSystem.get_cost_scene(wound, story_progress=0.45)
        
        print(f"\n{wound.value.upper()}:")
        print(f"  Victim: {scene['victim']}")
        print(f"  Type: {scene['consequence_type']}")
        print(f"  Harm: {scene['harm_description'][:50]}...")
        
        # Assertions
        assert scene['stage'] == "cost_revealed"
        assert scene['victim'] in ["Torres", "Kai", "Ember", "Vasquez"]
        assert len(scene['dialogue']) > 50
    
    print("\n✅ All archetype scenes verified")

def test_progress_gating():
    print("\n--- Testing Progress Gating ---")
    
    # Should fail with insufficient progress (< 40%)
    scene_early = CostRevealedSystem.get_cost_scene(
        WoundType.CONTROLLER, 
        story_progress=0.35
    )
    
    print(f"Early access (35%): {scene_early.get('error', 'NO ERROR')}")
    assert "error" in scene_early
    assert scene_early['required_progress'] == 0.40
    
    # Should succeed with sufficient progress
    scene_ready = CostRevealedSystem.get_cost_scene(
        WoundType.CONTROLLER,
        story_progress=0.42
    )
    
    print(f"Ready access (42%): Success = {'error' not in scene_ready}")
    assert "error" not in scene_ready
    
    print("✅ Progress gating verified")

def test_delivery_recording():
    print("\n--- Testing Delivery Recording ---")
    
    profile = WoundProfile(
        dominant_wound=WoundType.JUDGE,
        revelation_progress=0.25
    )
    
    record = CostRevealedSystem.record_delivery(
        profile,
        "test-scene-cost-789",
        WoundType.JUDGE
    )
    
    print(f"Progress updated to: {profile.revelation_progress}")
    
    assert profile.revelation_progress == 0.40
    assert len(profile.revelation_history) == 1
    assert profile.revelation_history[0].stage == "cost_revealed"
    assert profile.revelation_history[0].player_response == "confronted"
    
    print("✅ Delivery recording verified")

if __name__ == "__main__":
    try:
        test_all_archetype_scenes()
        test_progress_gating()
        test_delivery_recording()
        print("\n🎉 ALL COST REVEALED TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)
