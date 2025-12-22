"""
Verification script for archetype observation and inference layers.

This script tests:
1. Configuration loading
2. Behavior observation and signal extraction
3. Profile updating with decay and normalization
4. Need inference
5. Shift detection
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.archetype_config_loader import get_config_loader
from src.observation.archetype_observer import ArchetypeObserver
from src.inference.archetype_inference import ArchetypeInferenceEngine
from src.narrative.archetype_types import ArchetypeProfile


def test_config_loading():
    """Test that configuration loads correctly."""
    print("=" * 80)
    print("TEST 1: Configuration Loading")
    print("=" * 80)
    
    try:
        config = get_config_loader()
        archetypes = config.get_archetype_names()
        print(f"✓ Loaded {len(archetypes)} archetypes")
        print(f"  Archetypes: {', '.join(archetypes[:5])}...")
        
        # Test getting a specific archetype
        controller = config.get_archetype("controller")
        print(f"✓ Controller archetype:")
        print(f"  Psychological wound: {controller.psychological_wound}")
        print(f"  Moral corruption: {controller.moral_corruption}")
        
        # Test inference config
        inference_config = config.get_inference_config()
        print(f"✓ Inference config:")
        print(f"  Decay rate: {inference_config.decay_rate}")
        print(f"  Confidence threshold: {inference_config.confidence_threshold}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False


def test_observation():
    """Test behavior observation and signal extraction."""
    print("\n" + "=" * 80)
    print("TEST 2: Behavior Observation")
    print("=" * 80)
    
    try:
        observer = ArchetypeObserver()
        
        # Test 1: Controller dialogue
        print("\nTest 2.1: Controller dialogue")
        dialogue = "Tell me everything. I need to know exactly what happened."
        obs1 = observer.observe_dialogue(
            player_choice=dialogue,
            context="Interrogating Torres about the murder",
            scene_id="scene_001",
            npc_involved="Torres"
        )
        print(f"  Dialogue: '{dialogue}'")
        print(f"  Signals detected: {obs1.archetype_signals}")
        if "controller" in obs1.archetype_signals:
            print(f"  ✓ Controller signal: {obs1.archetype_signals['controller']}")
        
        # Test 2: Ghost dialogue
        print("\nTest 2.2: Ghost dialogue")
        dialogue2 = "That's not important. Let's talk about something else."
        obs2 = observer.observe_dialogue(
            player_choice=dialogue2,
            context="Ember asking about feelings",
            scene_id="scene_002",
            npc_involved="Ember"
        )
        print(f"  Dialogue: '{dialogue2}'")
        print(f"  Signals detected: {obs2.archetype_signals}")
        if "ghost" in obs2.archetype_signals:
            print(f"  ✓ Ghost signal: {obs2.archetype_signals['ghost']}")
        
        # Test 3: Destroyer action
        print("\nTest 2.3: Destroyer action")
        action = "Smash the console in frustration"
        obs3 = observer.observe_action(
            action_description=action,
            context="Failed to access the system",
            scene_id="scene_003"
        )
        print(f"  Action: '{action}'")
        print(f"  Signals detected: {obs3.archetype_signals}")
        if "destroyer" in obs3.archetype_signals:
            print(f"  ✓ Destroyer signal: {obs3.archetype_signals['destroyer']}")
        
        # Test 4: Cynic interrogation
        print("\nTest 2.4: Cynic interrogation")
        approach = "You're lying. Everyone lies. This won't work anyway."
        obs4 = observer.observe_interrogation(
            approach=approach,
            npc="Kai",
            context="Trying to get information",
            scene_id="scene_004"
        )
        print(f"  Approach: '{approach}'")
        print(f"  Signals detected: {obs4.archetype_signals}")
        if "cynic" in obs4.archetype_signals:
            print(f"  ✓ Cynic signal: {obs4.archetype_signals['cynic']}")
        
        return True
    except Exception as e:
        print(f"✗ Observation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_inference():
    """Test profile updating and inference."""
    print("\n" + "=" * 80)
    print("TEST 3: Profile Inference")
    print("=" * 80)
    
    try:
        observer = ArchetypeObserver()
        engine = ArchetypeInferenceEngine()
        
        # Start with empty profile
        profile = ArchetypeProfile()
        print(f"\nInitial profile:")
        print(f"  Primary: {profile.primary_archetype}")
        print(f"  Confidence: {profile.confidence:.2f}")
        
        # Simulate consistent controller behavior
        print("\nSimulating 5 controller behaviors...")
        observations = []
        controller_dialogues = [
            "Tell me everything right now.",
            "I demand an explanation.",
            "You must follow my orders.",
            "I need to know exactly what happened.",
            "This is unacceptable. Explain yourself."
        ]
        
        for i, dialogue in enumerate(controller_dialogues):
            obs = observer.observe_dialogue(
                player_choice=dialogue,
                context=f"Scene {i}",
                scene_id=f"scene_{i}",
            )
            observations.append(obs)
        
        # Update profile
        profile = engine.update_profile(profile, observations)
        
        print(f"\nAfter 5 controller behaviors:")
        print(f"  Primary: {profile.primary_archetype}")
        print(f"  Secondary: {profile.secondary_archetype}")
        print(f"  Confidence: {profile.confidence:.2f}")
        print(f"  Controller weight: {profile.controller:.3f}")
        print(f"  Overcontrolled tendency: {profile.overcontrolled_tendency:.3f}")
        print(f"  Observation count: {profile.observation_count}")
        
        # Test need inference
        print("\nInferring needs...")
        needs = engine.infer_needs(profile, observations)
        print(f"  Psychological wound: {needs.psychological_wound}")
        print(f"  Psychological need: {needs.psychological_need}")
        print(f"  Moral corruption: {needs.moral_corruption}")
        print(f"  Moral need: {needs.moral_need}")
        print(f"  Psychological awareness: {needs.psychological_awareness:.2f}")
        print(f"  Moral awareness: {needs.moral_awareness:.2f}")
        
        # Test decay
        print("\nTesting decay (updating with no new observations)...")
        old_weight = profile.controller
        profile = engine.update_profile(profile, [])
        new_weight = profile.controller
        print(f"  Controller weight before decay: {old_weight:.3f}")
        print(f"  Controller weight after decay: {new_weight:.3f}")
        print(f"  Decay applied: {(old_weight - new_weight):.3f}")
        
        return True
    except Exception as e:
        print(f"✗ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_shift_detection():
    """Test archetype shift detection."""
    print("\n" + "=" * 80)
    print("TEST 4: Shift Detection")
    print("=" * 80)
    
    try:
        observer = ArchetypeObserver()
        engine = ArchetypeInferenceEngine()
        
        # Build controller profile
        profile = ArchetypeProfile()
        controller_obs = [
            observer.observe_dialogue(
                "Tell me everything.", "Scene", f"scene_{i}"
            )
            for i in range(5)
        ]
        profile = engine.update_profile(profile, controller_obs)
        old_primary = profile.primary_archetype
        print(f"Initial primary archetype: {old_primary}")
        
        # Now add strong ghost signals
        print("\nAdding strong ghost signals...")
        ghost_obs = [
            observer.observe_dialogue(
                "That's not important. Let's change the subject.", "Scene", f"scene_{i+5}"
            )
            for i in range(10)
        ]
        
        new_profile = engine.update_profile(profile, ghost_obs)
        new_primary = new_profile.primary_archetype
        print(f"New primary archetype: {new_primary}")
        
        # Detect shift
        shift = engine.detect_shift(profile, new_profile)
        if shift:
            print(f"\n✓ Shift detected!")
            print(f"  From: {shift.old_primary}")
            print(f"  To: {shift.new_primary}")
            print(f"  Magnitude: {shift.shift_magnitude:.3f}")
        else:
            print("\n  No significant shift detected")
        
        return True
    except Exception as e:
        print(f"✗ Shift detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("ARCHETYPE SYSTEM VERIFICATION")
    print("=" * 80)
    
    results = []
    
    # Run tests
    results.append(("Configuration Loading", test_config_loading()))
    results.append(("Behavior Observation", test_observation()))
    results.append(("Profile Inference", test_inference()))
    results.append(("Shift Detection", test_shift_detection()))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
