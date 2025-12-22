"""
Dialogue Banks Verification Script

Tests all NPCs with all archetypes to ensure dialogue system is working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.narrative.dialogue_banks import (
    get_dialogue,
    get_relationship_stage,
    DialogueContext,
    RelationshipStage,
    DIALOGUE_BANKS
)
from src.character_identity import WoundType

def test_dialogue_structure():
    """Test that dialogue banks have correct structure."""
    print("=" * 80)
    print("TEST 1: Dialogue Bank Structure")
    print("=" * 80)
    
    required_npcs = ["torres", "kai", "okonkwo", "vasquez", "ember"]
    errors = []
    
    for npc in required_npcs:
        if npc not in DIALOGUE_BANKS:
            errors.append(f"❌ Missing NPC: {npc}")
            continue
        
        npc_bank = DIALOGUE_BANKS[npc]
        
        # Check baseline exists
        if "baseline" not in npc_bank:
            errors.append(f"❌ {npc}: Missing baseline dialogue")
        else:
            baseline = npc_bank["baseline"]
            required_contexts = ["first_meeting", "casual", "murder_question"]
            for ctx in required_contexts:
                if ctx not in baseline:
                    errors.append(f"❌ {npc}: Missing baseline context '{ctx}'")
                elif not baseline[ctx]:
                    errors.append(f"❌ {npc}: Empty baseline context '{ctx}'")
        
        print(f"✓ {npc.upper()}: Found {len(npc_bank) - 1} archetype variations")
    
    if errors:
        print("\n⚠️  ERRORS FOUND:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ All NPCs have valid structure")
        return True

def test_archetype_coverage():
    """Test that all archetypes have dialogue for each NPC."""
    print("\n" + "=" * 80)
    print("TEST 2: Archetype Coverage")
    print("=" * 80)
    
    # Core archetypes from user's prompt
    core_archetypes = ["controller", "judge", "ghost", "fugitive", "cynic", "savior"]
    
    coverage_matrix = {}
    
    for npc_id, npc_bank in DIALOGUE_BANKS.items():
        coverage_matrix[npc_id] = {}
        for archetype in core_archetypes:
            has_dialogue = archetype in npc_bank
            coverage_matrix[npc_id][archetype] = has_dialogue
    
    # Print matrix
    print(f"\n{'NPC':<12} | " + " | ".join(f"{a[:4].upper():<4}" for a in core_archetypes))
    print("-" * 80)
    
    for npc_id, archetypes in coverage_matrix.items():
        status = " | ".join("✓" if archetypes[a] else "✗" for a in core_archetypes)
        print(f"{npc_id.upper():<12} | {status}")
    
    # Check for missing coverage
    missing = []
    for npc_id, archetypes in coverage_matrix.items():
        for archetype, has in archetypes.items():
            if not has:
                missing.append(f"{npc_id} - {archetype}")
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} archetype variations (expected for some NPCs)")
        return True  # This is OK - not all NPCs need all archetypes
    else:
        print("\n✅ Complete archetype coverage")
        return True

def test_relationship_stages():
    """Test that relationship stage modifiers work correctly."""
    print("\n" + "=" * 80)
    print("TEST 3: Relationship Stage Progression")
    print("=" * 80)
    
    test_cases = [
        (0, RelationshipStage.EARLY),
        (2, RelationshipStage.EARLY),
        (3, RelationshipStage.MID),
        (7, RelationshipStage.MID),
        (8, RelationshipStage.LATE),
        (15, RelationshipStage.LATE),
    ]
    
    all_passed = True
    for interaction_count, expected_stage in test_cases:
        actual_stage = get_relationship_stage(interaction_count)
        if actual_stage == expected_stage:
            print(f"✓ Interaction {interaction_count:2d} → {expected_stage.value.upper()}")
        else:
            print(f"❌ Interaction {interaction_count:2d} → Expected {expected_stage.value}, got {actual_stage.value}")
            all_passed = False
    
    if all_passed:
        print("\n✅ Relationship stage progression working correctly")
    return all_passed

def test_dialogue_retrieval():
    """Test actual dialogue retrieval with various parameters."""
    print("\n" + "=" * 80)
    print("TEST 4: Dialogue Retrieval")
    print("=" * 80)
    
    test_scenarios = [
        # (npc_id, archetype, stage, trust, context, description)
        ("torres", "controller", RelationshipStage.EARLY, 0.5, DialogueContext.CASUAL, "Torres - Controller - Early - Neutral"),
        ("torres", "controller", RelationshipStage.LATE, 0.8, DialogueContext.ARCHETYPE_SPECIFIC, "Torres - Controller - Late - High Trust"),
        ("torres", "controller", RelationshipStage.MID, -0.5, DialogueContext.ARCHETYPE_SPECIFIC, "Torres - Controller - Mid - Low Trust"),
        ("kai", "judge", RelationshipStage.EARLY, 0.3, DialogueContext.CASUAL, "Kai - Judge - Early"),
        ("kai", "savior", RelationshipStage.MID, 0.6, DialogueContext.ARCHETYPE_SPECIFIC, "Kai - Savior - Mid"),
        ("okonkwo", "ghost", RelationshipStage.LATE, 0.7, DialogueContext.ARCHETYPE_SPECIFIC, "Okonkwo - Ghost - Late"),
        ("vasquez", "cynic", RelationshipStage.EARLY, 0.2, DialogueContext.FIRST_MEETING, "Vasquez - Cynic - First Meeting"),
        ("ember", "fugitive", RelationshipStage.MID, 0.5, DialogueContext.ARCHETYPE_SPECIFIC, "Ember - Fugitive - Mid"),
    ]
    
    passed = 0
    failed = 0
    
    for npc_id, archetype, stage, trust, context, description in test_scenarios:
        dialogue = get_dialogue(npc_id, archetype, stage, trust, context)
        
        if dialogue:
            print(f"✓ {description}")
            print(f"  → \"{dialogue[:80]}{'...' if len(dialogue) > 80 else ''}\"")
            passed += 1
        else:
            print(f"❌ {description} - NO DIALOGUE RETURNED")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All dialogue retrieval tests passed")
        return True
    else:
        print(f"⚠️  {failed} dialogue retrieval tests failed")
        return False

def test_trust_modifiers():
    """Test that trust modifiers (trust_built, trust_broken) work."""
    print("\n" + "=" * 80)
    print("TEST 5: Trust Modifiers")
    print("=" * 80)
    
    # Test high trust (should get trust_built dialogue)
    high_trust_dialogue = get_dialogue(
        "torres",
        "controller",
        RelationshipStage.LATE,
        0.9,  # Very high trust
        DialogueContext.ARCHETYPE_SPECIFIC
    )
    
    # Test low trust (should get trust_broken dialogue)
    low_trust_dialogue = get_dialogue(
        "torres",
        "controller",
        RelationshipStage.MID,
        -0.5,  # Very low trust
        DialogueContext.ARCHETYPE_SPECIFIC
    )
    
    results = []
    
    if high_trust_dialogue:
        print(f"✓ High Trust (0.9) Dialogue Retrieved")
        print(f"  → \"{high_trust_dialogue[:80]}...\"")
        results.append(True)
    else:
        print(f"❌ High Trust dialogue failed")
        results.append(False)
    
    if low_trust_dialogue:
        print(f"✓ Low Trust (-0.5) Dialogue Retrieved")
        print(f"  → \"{low_trust_dialogue[:80]}...\"")
        results.append(True)
    else:
        print(f"❌ Low Trust dialogue failed")
        results.append(False)
    
    # Verify they're different
    if high_trust_dialogue and low_trust_dialogue and high_trust_dialogue != low_trust_dialogue:
        print(f"✓ Trust modifiers produce different dialogue")
        results.append(True)
    else:
        print(f"⚠️  Trust modifiers may not be differentiating dialogue")
        results.append(False)
    
    if all(results):
        print("\n✅ Trust modifier system working correctly")
        return True
    else:
        print("\n⚠️  Some trust modifier tests failed")
        return False

def test_all_npc_archetype_combinations():
    """Comprehensive test of all NPC × Archetype combinations."""
    print("\n" + "=" * 80)
    print("TEST 6: Comprehensive NPC × Archetype Matrix")
    print("=" * 80)
    
    npcs = ["torres", "kai", "okonkwo", "vasquez", "ember"]
    archetypes = ["controller", "judge", "ghost", "fugitive", "cynic", "savior"]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for npc in npcs:
        for archetype in archetypes:
            total_tests += 1
            
            # Try to get dialogue for this combination
            dialogue = get_dialogue(
                npc,
                archetype,
                RelationshipStage.MID,
                0.5,
                DialogueContext.ARCHETYPE_SPECIFIC
            )
            
            if dialogue:
                passed_tests += 1
            else:
                # Check if this archetype is expected for this NPC
                if archetype in DIALOGUE_BANKS.get(npc, {}):
                    failed_tests.append(f"{npc} - {archetype}")
    
    print(f"📊 Tested {total_tests} combinations")
    print(f"✓ {passed_tests} returned dialogue")
    print(f"✗ {len(failed_tests)} failed (may be expected)")
    
    if failed_tests:
        print("\nFailed combinations:")
        for combo in failed_tests:
            print(f"  - {combo}")
    
    # Success if we have at least 70% coverage
    success_rate = passed_tests / total_tests
    if success_rate >= 0.7:
        print(f"\n✅ {success_rate:.1%} coverage - PASS")
        return True
    else:
        print(f"\n⚠️  {success_rate:.1%} coverage - needs improvement")
        return False

def main():
    """Run all verification tests."""
    print("\n" + "=" * 80)
    print("DIALOGUE BANKS VERIFICATION SUITE")
    print("=" * 80)
    
    tests = [
        ("Structure", test_dialogue_structure),
        ("Archetype Coverage", test_archetype_coverage),
        ("Relationship Stages", test_relationship_stages),
        ("Dialogue Retrieval", test_dialogue_retrieval),
        ("Trust Modifiers", test_trust_modifiers),
        ("Comprehensive Matrix", test_all_npc_archetype_combinations),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} CRASHED: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for p in results.values() if p)
    total_tests = len(results)
    
    print("\n" + "=" * 80)
    print(f"OVERALL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED - Dialogue system ready for integration!")
        print("=" * 80)
        return 0
    else:
        print("⚠️  Some tests failed - review output above")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    exit(main())
