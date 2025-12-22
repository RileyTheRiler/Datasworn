import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.psych_profile import PsychologicalProfile, PsychologicalEngine
from src.character_identity import WoundType, RUOType

def verify_deep_psychology():
    print("=== Verifying Deep Psychology System (22 Archetypes) ===")
    
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Test Cases for specific archetypes
    test_cases = [
        {
            "input": "I have to examine the evidence. Every detail matters. I can't let chaos rule this ship.",
            "expected_wound": WoundType.CONTROLLER,
            "expected_ruo": RUOType.OVERCONTROLLED
        },
        {
            "input": "They are guilty. I know it. They must pay for what they did.",
            "expected_wound": WoundType.JUDGE,
            "expected_ruo": RUOType.OVERCONTROLLED
        },
        {
            "input": "I don't care about them. Everyone leaves eventually. It's better to be alone.",
            "expected_wound": WoundType.GHOST,
            "expected_ruo": RUOType.OVERCONTROLLED
        },
        {
            "input": "I have to keep running. If I stop, my past will catch up with me.",
            "expected_wound": WoundType.FUGITIVE,
            "expected_ruo": RUOType.UNDERCONTROLLED
        },
        {
            "input": "Everyone is lying. You can't trust anyone in this universe.",
            "expected_wound": WoundType.CYNIC,
            "expected_ruo": RUOType.UNDERCONTROLLED
        },
        {
            "input": "Burn it all down! There is no justice, only fire!",
            "expected_wound": WoundType.DESTROYER,
            "expected_ruo": RUOType.UNDERCONTROLLED
        }
    ]
    
    for case in test_cases:
        print(f"\nTesting Input: '{case['input']}'")
        
        # Reset profile scores for clean test
        profile = PsychologicalProfile() 
        
        # Update twice to build score (since dampening is 0.1)
        engine.update_wound_profile(profile, case['input'])
        engine.update_wound_profile(profile, case['input'])
        engine.update_wound_profile(profile, case['input'])
        
        dominant = profile.identity.wound_profile.dominant_wound
        scores = profile.identity.wound_profile.scores.to_dict()
        
        print(f"  -> Dominant Wound: {dominant}")
        print(f"  -> Expected: {case['expected_wound']}")
        
        if dominant == case['expected_wound']:
            print("  [PASS] Wound Detection")
        else:
            print(f"  [FAIL] Wound Detection. Scores: {scores}")

        # Verify Derived Content
        lens = engine.get_thematic_lens(profile)
        ember = engine.get_ember_dialogue(profile)
        wisdom = engine.get_dark_wisdom(profile)
        
        if lens and ember and wisdom:
            print("  [PASS] Derived Content Generation")
            print(f"    Lens: {lens[:50]}...")
            print(f"    Ember: {ember[:50]}...")
            print(f"    Wisdom: {wisdom[:50]}...")
        else:
            print("  [FAIL] Derived Content Missing")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify_deep_psychology()
