"""
Verification script for Scene Templates System.

Tests:
1. All scene template endpoints
2. Data structure completeness
3. Scene generation with different archetypes
4. Archetype-specific variations
5. NPC integration points
6. Beat structure integrity
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8001"

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_success(message: str):
    """Print a success message."""
    print(f"✓ {message}")

def print_error(message: str):
    """Print an error message."""
    print(f"✗ {message}")

def print_info(message: str):
    """Print an info message."""
    print(f"  {message}")

def test_list_scene_templates():
    """Test 1: List all available scene templates."""
    print_section("TEST 1: List Scene Templates")
    
    try:
        response = requests.get(f"{BASE_URL}/api/narrative/scene-templates/list")
        response.raise_for_status()
        data = response.json()
        
        scene_types = data.get("scene_types", [])
        
        if len(scene_types) == 9:
            print_success(f"Found all 9 scene types")
        else:
            print_error(f"Expected 9 scene types, found {len(scene_types)}")
            return False
        
        # Verify categories
        crisis_count = sum(1 for st in scene_types if st['category'] == 'crisis')
        quiet_count = sum(1 for st in scene_types if st['category'] == 'quiet')
        revelation_count = sum(1 for st in scene_types if st['category'] == 'revelation')
        
        print_info(f"Crisis Moments: {crisis_count}")
        print_info(f"Quiet Moments: {quiet_count}")
        print_info(f"Revelation Moments: {revelation_count}")
        
        if crisis_count == 3 and quiet_count == 3 and revelation_count == 3:
            print_success("Scene type distribution correct (3-3-3)")
        else:
            print_error(f"Scene type distribution incorrect")
            return False
        
        # Print all scene types
        print_info("\nAvailable Scene Types:")
        for st in scene_types:
            print_info(f"  - {st['name']} ({st['scene_type']})")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to list scene templates: {e}")
        return False

def test_scene_template_details():
    """Test 2: Get detailed information for each scene type."""
    print_section("TEST 2: Scene Template Details")
    
    scene_types = [
        "crisis_system_failure",
        "crisis_confrontation",
        "crisis_accusation",
        "quiet_shared_silence",
        "quiet_confession",
        "quiet_question",
        "revelation_mirror",
        "revelation_cost",
        "revelation_naming"
    ]
    
    all_passed = True
    
    for scene_type in scene_types:
        try:
            response = requests.get(f"{BASE_URL}/api/narrative/scene-templates/{scene_type}")
            response.raise_for_status()
            data = response.json()
            
            # Verify structure
            required_fields = ["scene_type", "name", "purpose", "trigger_conditions", "beats"]
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print_error(f"{scene_type}: Missing fields {missing_fields}")
                all_passed = False
                continue
            
            # Verify beats
            beats = data.get("beats", [])
            if len(beats) != 5:
                print_error(f"{scene_type}: Expected 5 beats, found {len(beats)}")
                all_passed = False
                continue
            
            # Verify beat structure
            for beat in beats:
                required_beat_fields = ["beat_number", "beat_name", "description", "narrative_text"]
                missing_beat_fields = [f for f in required_beat_fields if f not in beat]
                if missing_beat_fields:
                    print_error(f"{scene_type} beat {beat.get('beat_number', '?')}: Missing {missing_beat_fields}")
                    all_passed = False
            
            print_success(f"{data['name']}: Structure valid, {len(beats)} beats")
            
        except Exception as e:
            print_error(f"{scene_type}: {e}")
            all_passed = False
    
    return all_passed

def test_scene_generation_archetypes():
    """Test 3: Generate scenes for different archetypes."""
    print_section("TEST 3: Scene Generation with Different Archetypes")
    
    # First, create a test session
    try:
        init_response = requests.post(f"{BASE_URL}/api/init", json={
            "character_name": "Test Character",
            "background_vow": "Test the scene templates",
            "stats": {"edge": 2, "heart": 2, "iron": 2, "shadow": 2, "wits": 2}
        })
        init_response.raise_for_status()
        session_data = init_response.json()
        session_id = session_data.get("session_id", "default")
        print_info(f"Created test session: {session_id}")
    except Exception as e:
        print_error(f"Failed to create test session: {e}")
        return False
    
    # Test scene generation
    test_cases = [
        {"scene_type": "crisis_system_failure", "npc_id": "kai"},
        {"scene_type": "crisis_confrontation", "npc_id": "torres_vs_kai"},
        {"scene_type": "quiet_shared_silence", "npc_id": "ember"},
        {"scene_type": "quiet_confession", "npc_id": "okonkwo"},
        {"scene_type": "revelation_mirror", "npc_id": None},
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        try:
            payload = {
                "session_id": session_id,
                "scene_type": test_case["scene_type"],
                "npc_id": test_case["npc_id"]
            }
            
            response = requests.post(
                f"{BASE_URL}/api/narrative/scene-templates/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            # Verify generated scene
            required_fields = ["scene_type", "name", "purpose", "player_archetype", "beats"]
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print_error(f"{test_case['scene_type']}: Missing fields {missing_fields}")
                all_passed = False
                continue
            
            # Check for archetype-specific content
            has_archetype_guidance = "archetype_guidance" in data
            has_npc_variation = "npc_variation" in data if test_case["npc_id"] else True
            
            status = "✓" if has_archetype_guidance and has_npc_variation else "⚠"
            print_info(f"{status} {data['name']}")
            print_info(f"   Archetype: {data['player_archetype']}")
            if test_case["npc_id"]:
                print_info(f"   NPC: {data.get('npc_variation', 'N/A')}")
            if "choices" in data:
                print_info(f"   Choices: {len(data['choices'])}")
            
            print_success(f"{test_case['scene_type']}: Generated successfully")
            
        except Exception as e:
            print_error(f"{test_case['scene_type']}: {e}")
            all_passed = False
    
    return all_passed

def test_archetype_variations():
    """Test 4: Verify archetype-specific variations exist."""
    print_section("TEST 4: Archetype-Specific Variations")
    
    archetypes_to_test = ["controller", "judge", "ghost", "savior", "cynic"]
    scenes_with_variations = [
        "crisis_system_failure",
        "crisis_confrontation",
        "quiet_shared_silence",
        "revelation_mirror"
    ]
    
    all_passed = True
    
    for scene_type in scenes_with_variations:
        try:
            response = requests.get(f"{BASE_URL}/api/narrative/scene-templates/{scene_type}")
            response.raise_for_status()
            data = response.json()
            
            archetype_integration = data.get("archetype_integration", {})
            
            if len(archetype_integration) > 0:
                print_success(f"{data['name']}: {len(archetype_integration)} archetype integrations")
                for archetype in archetypes_to_test:
                    if archetype in archetype_integration:
                        print_info(f"   ✓ {archetype}")
            else:
                print_error(f"{data['name']}: No archetype integrations found")
                all_passed = False
                
        except Exception as e:
            print_error(f"{scene_type}: {e}")
            all_passed = False
    
    return all_passed

def test_npc_integration():
    """Test 5: Verify NPC-specific variations."""
    print_section("TEST 5: NPC Integration Points")
    
    npc_scenes = [
        ("crisis_system_failure", ["kai", "torres"]),
        ("crisis_confrontation", ["torres_vs_kai"]),
        ("quiet_shared_silence", ["ember"]),
        ("quiet_confession", ["okonkwo"]),
        ("quiet_question", ["kai"])
    ]
    
    all_passed = True
    
    for scene_type, expected_npcs in npc_scenes:
        try:
            response = requests.get(f"{BASE_URL}/api/narrative/scene-templates/{scene_type}")
            response.raise_for_status()
            data = response.json()
            
            npc_variations = data.get("npc_variations", [])
            
            found_npcs = set(npc_variations)
            expected_npcs_set = set(expected_npcs)
            
            if found_npcs >= expected_npcs_set:
                print_success(f"{data['name']}: NPC variations present")
                for npc in npc_variations:
                    print_info(f"   - {npc}")
            else:
                missing = expected_npcs_set - found_npcs
                print_error(f"{data['name']}: Missing NPC variations: {missing}")
                all_passed = False
                
        except Exception as e:
            print_error(f"{scene_type}: {e}")
            all_passed = False
    
    return all_passed

def test_beat_structure():
    """Test 6: Verify beat structure integrity."""
    print_section("TEST 6: Beat Structure Integrity")
    
    all_passed = True
    
    # Test a few representative scenes
    test_scenes = [
        "crisis_system_failure",
        "quiet_confession",
        "revelation_naming"
    ]
    
    for scene_type in test_scenes:
        try:
            response = requests.get(f"{BASE_URL}/api/narrative/scene-templates/{scene_type}")
            response.raise_for_status()
            data = response.json()
            
            beats = data.get("beats", [])
            
            # Verify beat numbers are sequential
            beat_numbers = [beat["beat_number"] for beat in beats]
            expected_numbers = list(range(1, 6))
            
            if beat_numbers == expected_numbers:
                print_success(f"{data['name']}: Beat sequence correct (1-5)")
            else:
                print_error(f"{data['name']}: Beat sequence incorrect: {beat_numbers}")
                all_passed = False
                continue
            
            # Verify each beat has required fields
            for beat in beats:
                if not beat.get("narrative_text"):
                    print_error(f"{data['name']} Beat {beat['beat_number']}: Missing narrative text")
                    all_passed = False
            
            print_info(f"   All beats have narrative content")
            
        except Exception as e:
            print_error(f"{scene_type}: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all verification tests."""
    print_section("SCENE TEMPLATES VERIFICATION SCRIPT")
    print_info("Testing backend endpoints before frontend integration")
    print_info(f"Base URL: {BASE_URL}")
    
    results = []
    
    # Run all tests
    results.append(("List Scene Templates", test_list_scene_templates()))
    results.append(("Scene Template Details", test_scene_template_details()))
    results.append(("Scene Generation (Archetypes)", test_scene_generation_archetypes()))
    results.append(("Archetype Variations", test_archetype_variations()))
    results.append(("NPC Integration", test_npc_integration()))
    results.append(("Beat Structure", test_beat_structure()))
    
    # Print summary
    print_section("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print_success("\nALL TESTS PASSED! Backend is ready for frontend integration.")
        return 0
    else:
        print_error(f"\n{total - passed} test(s) failed. Fix issues before proceeding to frontend.")
        return 1

if __name__ == "__main__":
    exit(main())
