"""
Integration Verification Script
Tests that secondary characters are properly integrated into game systems.
"""

import sys
import os
import json

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.relationship_system import RelationshipWeb
    from src.narrative.revelation_manager import RevelationManager
    from src.narrative.secondary_characters import SECONDARY_CHARACTERS
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

def test_relationship_web_integration():
    """Test that RelationshipWeb loads secondary character data."""
    print("\n--- Testing RelationshipWeb Integration ---")
    
    web = RelationshipWeb()
    
    # Check that crew members are loaded
    if len(web.crew) != 6:
        print(f"FAILED: Expected 6 crew members, got {len(web.crew)}")
        return False
    
    # Check Torres specifically
    torres = web.crew.get("pilot")
    if not torres:
        print("FAILED: Torres not found in crew")
        return False
    
    if torres.name != "Elena Torres":
        print(f"FAILED: Torres name is '{torres.name}', expected 'Elena Torres'")
        return False
    
    # Check that secret knowledge is loaded
    if not torres.secrets:
        print("FAILED: Torres has no secrets")
        return False
    
    if "Yuki" not in torres.secrets[0]:
        print(f"FAILED: Torres secret doesn't mention Yuki: {torres.secrets[0]}")
        return False
    
    # Check description
    if not torres.description:
        print("FAILED: Torres has no description")
        return False
    
    if "military" not in torres.description.lower():
        print(f"FAILED: Torres description doesn't mention military: {torres.description}")
        return False
    
    print("SUCCESS: RelationshipWeb integration verified")
    return True

def test_revelation_manager():
    """Test RevelationManager functionality."""
    print("\n--- Testing RevelationManager ---")
    
    manager = RevelationManager()
    
    # Check initialization
    if len(manager.states) != 5:
        print(f"FAILED: Expected 5 character states, got {len(manager.states)}")
        return False
    
    # Test revelation check - Torres + military topic
    context = {"topic": "military service", "trust_score": 0.5}
    revelation = manager.check_for_revelations("torres", context)
    
    if not revelation:
        print("FAILED: Torres military revelation should trigger")
        return False
    
    if revelation.id != "torres_brother":
        print(f"FAILED: Expected 'torres_brother', got '{revelation.id}'")
        return False
    
    # Test marking as revealed
    success = manager.trigger_revelation("torres", "torres_brother")
    if not success:
        print("FAILED: Could not mark revelation as revealed")
        return False
    
    # Test that it doesn't trigger again
    revelation2 = manager.check_for_revelations("torres", context)
    if revelation2:
        print("FAILED: Revelation triggered again after being marked revealed")
        return False
    
    # Test unrevealed count
    unrevealed = manager.get_unrevealed_count("torres")
    if unrevealed != 1:  # Torres has 2 revelations, 1 is now revealed
        print(f"FAILED: Expected 1 unrevealed, got {unrevealed}")
        return False
    
    print("SUCCESS: RevelationManager verified")
    return True

def test_serialization():
    """Test that RevelationManager can serialize/deserialize."""
    print("\n--- Testing Serialization ---")
    
    manager = RevelationManager()
    manager.trigger_revelation("torres", "torres_brother")
    manager.trigger_revelation("kai", "kai_accident")
    
    # Serialize
    data = manager.to_dict()
    
    # Deserialize
    manager2 = RevelationManager.from_dict(data)
    
    # Verify state preserved
    if not manager2.is_revealed("torres", "torres_brother"):
        print("FAILED: Torres revelation not preserved after deserialization")
        return False
    
    if not manager2.is_revealed("kai", "kai_accident"):
        print("FAILED: Kai revelation not preserved after deserialization")
        return False
    
    if manager2.is_revealed("torres", "torres_sighting"):
        print("FAILED: Unrevealed revelation marked as revealed after deserialization")
        return False
    
    print("SUCCESS: Serialization verified")
    return True

def test_summary():
    """Test revelation summary generation."""
    print("\n--- Testing Summary Generation ---")
    
    manager = RevelationManager()
    manager.trigger_revelation("torres", "torres_brother")
    
    summary = manager.get_summary()
    
    if "torres" not in summary:
        print("FAILED: Torres not in summary")
        return False
    
    torres_summary = summary["torres"]
    if torres_summary["revealed_count"] != 1:
        print(f"FAILED: Expected 1 revealed, got {torres_summary['revealed_count']}")
        return False
    
    if torres_summary["unrevealed_count"] != 1:
        print(f"FAILED: Expected 1 unrevealed, got {torres_summary['unrevealed_count']}")
        return False
    
    print("SUCCESS: Summary generation verified")
    return True

def main():
    print("Starting Secondary Character Integration Verification...")
    
    results = [
        test_relationship_web_integration(),
        test_revelation_manager(),
        test_serialization(),
        test_summary()
    ]
    
    if all(results):
        print("\n✓ ALL INTEGRATION TESTS PASSED")
    else:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
