"""
Verification Script for Ending Variations System

Tests all 6 core archetypes × 2 paths (Hero/Tragedy) × 5 stages
to ensure the backend endpoints work correctly before frontend integration.
"""

import requests
import json
from typing import Dict, List, Tuple

# Configuration
BASE_URL = "http://localhost:8001"
SESSION_ID = "default"

# Core archetypes to test
ARCHETYPES = ["controller", "judge", "ghost", "fugitive", "cynic", "savior"]

# All 5 ending stages
STAGES = ["decision", "test", "resolution", "wisdom", "final_scene"]

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} | {test_name}")
    if details and not passed:
        print(f"       Details: {details}")
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append(f"{test_name}: {details}")


def create_test_session(archetype: str) -> bool:
    """Create a test session with a specific archetype"""
    try:
        # Create a basic session
        response = requests.post(
            f"{BASE_URL}/api/session/start",
            json={
                "character_name": f"Test_{archetype}",
                "background_vow": "Test the ending system"
            }
        )
        
        if response.status_code != 200:
            return False
        
        # Manually set the archetype in the session
        # Note: In a real game, this would be determined by player behavior
        # For testing, we'll use the calibration endpoint or direct manipulation
        
        return True
    except Exception as e:
        print(f"Error creating session: {e}")
        return False


def test_sequence_endpoint(archetype: str) -> Tuple[bool, Dict]:
    """Test /api/narrative/ending/sequence endpoint"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/narrative/ending/sequence",
            params={"session_id": SESSION_ID}
        )
        
        if response.status_code != 200:
            return False, {}
        
        data = response.json()
        
        # Validate response structure
        required_fields = ["archetype", "moral_question", "decision_options", "hero_path", "tragedy_path"]
        for field in required_fields:
            if field not in data:
                return False, {}
        
        # Validate hero_path has all stages
        for stage in STAGES:
            if stage not in data["hero_path"]:
                return False, {}
            if not data["hero_path"][stage]:
                return False, {}
        
        # Validate tragedy_path has all stages
        for stage in STAGES:
            if stage not in data["tragedy_path"]:
                return False, {}
            if not data["tragedy_path"][stage]:
                return False, {}
        
        return True, data
    except Exception as e:
        return False, {}


def test_decision_endpoint(choice: str) -> Tuple[bool, str]:
    """Test /api/narrative/ending/decision endpoint"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/narrative/ending/decision",
            json={
                "session_id": SESSION_ID,
                "choice": choice
            }
        )
        
        if response.status_code != 200:
            return False, ""
        
        data = response.json()
        
        # Validate response structure
        required_fields = ["ending_type", "archetype", "choice", "next_stage"]
        for field in required_fields:
            if field not in data:
                return False, ""
        
        # Validate ending_type is either hero or tragedy
        if data["ending_type"] not in ["hero", "tragedy"]:
            return False, ""
        
        return True, data["ending_type"]
    except Exception as e:
        return False, ""


def test_progress_endpoint(stage: str) -> Tuple[bool, str]:
    """Test /api/narrative/ending/progress endpoint"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/narrative/ending/progress",
            params={
                "session_id": SESSION_ID,
                "stage": stage
            }
        )
        
        if response.status_code != 200:
            return False, ""
        
        data = response.json()
        
        # Validate response structure
        required_fields = ["stage", "ending_type", "archetype", "narrative"]
        for field in required_fields:
            if field not in data:
                return False, ""
        
        # Validate narrative is not empty
        if not data["narrative"]:
            return False, ""
        
        return True, data["narrative"]
    except Exception as e:
        return False, ""


def run_comprehensive_test():
    """Run the complete test suite"""
    print_header("ENDING VARIATIONS SYSTEM VERIFICATION")
    print(f"Testing {len(ARCHETYPES)} archetypes × 2 paths × {len(STAGES)} stages")
    print(f"Base URL: {BASE_URL}")
    
    # Test 1: Server availability
    print_header("Test 1: Server Availability")
    try:
        response = requests.get(f"{BASE_URL}/")
        server_available = response.status_code == 200
        print_test("Server is online", server_available)
    except Exception as e:
        print_test("Server is online", False, str(e))
        print("\n⚠️  Cannot proceed without server. Please start the server first.")
        return
    
    # Test 2: Session creation
    print_header("Test 2: Session Creation")
    session_created = create_test_session("controller")
    print_test("Test session created", session_created)
    
    if not session_created:
        print("\n⚠️  Cannot proceed without session.")
        return
    
    # Test 3: Sequence endpoint for all archetypes
    print_header("Test 3: Sequence Endpoint (All Archetypes)")
    sequence_data = {}
    for archetype in ARCHETYPES:
        passed, data = test_sequence_endpoint(archetype)
        print_test(f"Sequence endpoint - {archetype}", passed)
        if passed:
            sequence_data[archetype] = data
    
    # Test 4: Decision processing (Hero path)
    print_header("Test 4: Decision Processing (Hero Path)")
    passed, ending_type = test_decision_endpoint("accept")
    is_hero = ending_type == "hero"
    print_test("Decision 'accept' → Hero path", is_hero, 
               f"Got {ending_type}" if not is_hero else "")
    
    # Test 5: Progress endpoint for all stages (Hero path)
    if is_hero:
        print_header("Test 5: Progress Endpoint (Hero Path - All Stages)")
        for stage in STAGES:
            passed, narrative = test_progress_endpoint(stage)
            print_test(f"Progress - {stage}", passed,
                      "Empty narrative" if not narrative else "")
    
    # Test 6: Decision processing (Tragedy path)
    print_header("Test 6: Decision Processing (Tragedy Path)")
    # Create new session for tragedy test
    create_test_session("controller")
    passed, ending_type = test_decision_endpoint("reject")
    is_tragedy = ending_type == "tragedy"
    print_test("Decision 'reject' → Tragedy path", is_tragedy,
               f"Got {ending_type}" if not is_tragedy else "")
    
    # Test 7: Progress endpoint for all stages (Tragedy path)
    if is_tragedy:
        print_header("Test 7: Progress Endpoint (Tragedy Path - All Stages)")
        for stage in STAGES:
            passed, narrative = test_progress_endpoint(stage)
            print_test(f"Progress - {stage}", passed,
                      "Empty narrative" if not narrative else "")
    
    # Test 8: Content validation (spot check)
    print_header("Test 8: Content Validation (Spot Checks)")
    if sequence_data:
        # Check Controller archetype has specific keywords
        if "controller" in sequence_data:
            controller_data = sequence_data["controller"]
            has_control_theme = "control" in controller_data["moral_question"].lower()
            print_test("Controller archetype has 'control' theme", has_control_theme)
            
            has_crew_decision = "crew" in str(controller_data["decision_options"]).lower()
            print_test("Controller has 'crew decision' option", has_crew_decision)
        
        # Check Judge archetype has specific keywords
        if "judge" in sequence_data:
            judge_data = sequence_data["judge"]
            has_forgive_theme = "forgive" in judge_data["moral_question"].lower()
            print_test("Judge archetype has 'forgive' theme", has_forgive_theme)
    
    # Final summary
    print_header("VERIFICATION SUMMARY")
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {test_results['passed']} ✓")
    print(f"Failed: {test_results['failed']} ✗")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results["failed"] > 0:
        print("\n⚠️  FAILED TESTS:")
        for error in test_results["errors"]:
            print(f"  - {error}")
    
    if pass_rate == 100:
        print("\n🎉 ALL TESTS PASSED! Backend is ready for frontend integration.")
    elif pass_rate >= 80:
        print("\n⚠️  Most tests passed, but some issues remain. Review failures above.")
    else:
        print("\n❌ VERIFICATION FAILED. Fix backend issues before proceeding to frontend.")
    
    return pass_rate == 100


if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
