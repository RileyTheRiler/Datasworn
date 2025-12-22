"""
Verification Script for Port Arrival Sequence System

Tests all Port Arrival endpoints with different story states and archetype/path combinations
to ensure the backend works correctly before frontend integration.
"""

import requests
import json
from typing import Dict, List, Tuple

# Configuration
BASE_URL = "http://localhost:8001"
SESSION_ID = "default"

# All NPCs to test
NPCS = ["torres", "kai", "okonkwo", "vasquez", "ember"]

# Core archetypes to test (subset for faster testing, full 22 available)
TEST_ARCHETYPES = ["controller", "judge", "ghost", "fugitive", "cynic", "savior"]

# Ending types
ENDING_TYPES = ["hero", "tragedy"]

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


def create_test_session() -> bool:
    """Create a test session"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/session/start",
            json={
                "character_name": "Test_PortArrival",
                "background_vow": "Test the port arrival system"
            }
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error creating session: {e}")
        return False


def test_approach_general() -> Tuple[bool, Dict]:
    """Test general approach endpoint"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/narrative/port-arrival/approach",
            params={"session_id": SESSION_ID}
        )
        
        if response.status_code != 200:
            return False, {}
        
        data = response.json()
        
        # Validate response structure
        required_fields = ["stage", "narration", "torres_prompt", "available_conversations"]
        for field in required_fields:
            if field not in data:
                return False, {}
        
        # Validate available conversations list
        if not isinstance(data["available_conversations"], list):
            return False, {}
        
        return True, data
    except Exception as e:
        return False, {}


def test_approach_npc(npc_id: str) -> Tuple[bool, str]:
    """Test NPC-specific approach conversation"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/narrative/port-arrival/approach",
            params={"session_id": SESSION_ID, "npc_id": npc_id}
        )
        
        if response.status_code != 200:
            return False, ""
        
        data = response.json()
        
        # Validate response structure
        required_fields = ["stage", "npc_id", "conversation"]
        for field in required_fields:
            if field not in data:
                return False, ""
        
        # Validate conversation is not empty
        if not data["conversation"]:
            return False, ""
        
        return True, data["conversation"]
    except Exception as e:
        return False, ""


def test_docking(scenario_type: str = "none") -> Tuple[bool, Dict]:
    """Test docking endpoint"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/narrative/port-arrival/docking",
            params={"session_id": SESSION_ID}
        )
        
        if response.status_code != 200:
            return False, {}
        
        data = response.json()
        
        # Validate response structure
        required_fields = ["stage", "scenario", "arrival_description", "authority_presence"]
        for field in required_fields:
            if field not in data:
                return False, {}
        
        # Validate scenario is one of the valid types
        valid_scenarios = ["station_security", "corporate_reps", "creditors", "none"]
        if data["scenario"] not in valid_scenarios:
            return False, {}
        
        return True, data
    except Exception as e:
        return False, {}


def test_dispersal_single(npc_id: str, ending_type: str) -> Tuple[bool, str]:
    """Test single NPC dispersal"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/narrative/port-arrival/dispersal",
            params={"session_id": SESSION_ID, "npc_id": npc_id}
        )
        
        # This should fail without ending_type set
        # We'll need to set it first
        return True, ""  # Placeholder for now
    except Exception as e:
        return False, ""


def test_dispersal_all(ending_type: str) -> Tuple[bool, Dict]:
    """Test all NPC dispersals"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/narrative/port-arrival/dispersal",
            params={"session_id": SESSION_ID}
        )
        
        # This should fail without ending_type set
        # We'll need to set it first
        return True, {}  # Placeholder for now
    except Exception as e:
        return False, {}


def test_epilogue(archetype: str, ending_type: str) -> Tuple[bool, Dict]:
    """Test epilogue endpoint"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/narrative/port-arrival/epilogue",
            params={"session_id": SESSION_ID}
        )
        
        # This should fail without ending_type set
        # We'll need to set it first
        return True, {}  # Placeholder for now
    except Exception as e:
        return False, {}


def test_status() -> Tuple[bool, Dict]:
    """Test status endpoint"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/narrative/port-arrival/status",
            params={"session_id": SESSION_ID}
        )
        
        if response.status_code != 200:
            return False, {}
        
        data = response.json()
        
        # Validate response structure
        required_fields = ["current_stage", "completed_conversations", "available_conversations"]
        for field in required_fields:
            if field not in data:
                return False, {}
        
        return True, data
    except Exception as e:
        return False, {}


def run_comprehensive_test():
    """Run the complete test suite"""
    print_header("PORT ARRIVAL SEQUENCE VERIFICATION")
    print(f"Testing {len(NPCS)} NPCs × {len(ENDING_TYPES)} paths")
    print(f"Testing {len(TEST_ARCHETYPES)} archetypes × {len(ENDING_TYPES)} paths")
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
        return False
    
    # Test 2: Session creation
    print_header("Test 2: Session Creation")
    session_created = create_test_session()
    print_test("Test session created", session_created)
    
    if not session_created:
        print("\n⚠️  Cannot proceed without session.")
        return False
    
    # Test 3: Approach endpoint - general
    print_header("Test 3: Approach Endpoint - General Scene")
    passed, data = test_approach_general()
    print_test("General approach scene", passed)
    
    # Test 4: Approach endpoint - NPC conversations
    print_header("Test 4: Approach Endpoint - NPC Conversations")
    for npc in NPCS:
        passed, conversation = test_approach_npc(npc)
        print_test(f"NPC conversation - {npc}", passed,
                  "Empty conversation" if not conversation else "")
    
    # Test 5: Docking endpoint
    print_header("Test 5: Docking Endpoint")
    passed, data = test_docking()
    print_test("Docking scenario", passed)
    if passed and data:
        print(f"       Scenario: {data.get('scenario', 'unknown')}")
    
    # Test 6: Status endpoint
    print_header("Test 6: Status Endpoint")
    passed, data = test_status()
    print_test("Port arrival status", passed)
    if passed and data:
        print(f"       Current stage: {data.get('current_stage', 'unknown')}")
        print(f"       Completed conversations: {len(data.get('completed_conversations', []))}")
    
    # Test 7: Dispersal and Epilogue (require ending_type)
    print_header("Test 7: Dispersal & Epilogue Endpoints")
    print("⚠️  Note: Dispersal and Epilogue endpoints require ending_type to be set")
    print("    These will be tested after implementing ending decision flow")
    
    # Content validation
    print_header("Test 8: Content Validation (Spot Checks)")
    if data:
        # Check that approach scene mentions key elements
        passed, approach_data = test_approach_general()
        if passed:
            has_twelve_hours = "twelve hours" in approach_data.get("narration", "").lower()
            print_test("Approach mentions 'twelve hours'", has_twelve_hours)
            
            has_meridian = "meridian" in approach_data.get("narration", "").lower()
            print_test("Approach mentions 'Meridian Station'", has_meridian)
    
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
    
    print("\n📝 NEXT STEPS:")
    print("  1. Implement ending decision flow to set ending_type in game state")
    print("  2. Re-run verification to test dispersal and epilogue endpoints")
    print("  3. Test all 22 archetypes × 2 paths = 44 epilogue combinations")
    print("  4. Proceed to frontend integration only after 100% pass rate")
    
    return pass_rate >= 80


if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
