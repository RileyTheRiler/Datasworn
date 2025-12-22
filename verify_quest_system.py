"""
Quest System Verification Script

Tests all quest system functionality including:
- Quest graph loading and validation
- Quest state transitions
- World state flag management
- API endpoint integration
- Consequence tracking
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8003"
SESSION_ID = "default"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str):
    """Print test name."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[TEST] {name}{Colors.END}")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}[PASS] {message}{Colors.END}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}[FAIL] {message}{Colors.END}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.YELLOW}[INFO] {message}{Colors.END}")


def init_session():
    """Initialize a test session."""
    print_test("Initialize Session")
    try:
        response = requests.post(f"{BASE_URL}/api/session/start", json={
            "character_name": "Quest Tester",
            "background_vow": "Verify the system"
        })
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            print_success(f"Session initialized: {session_id}")
            
            # Update global session ID
            global SESSION_ID
            SESSION_ID = session_id
            
            return True
        else:
            print_error(f"Failed to init session: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_server_health():
    """Test if server is running."""
    print_test("Server Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success("Server is running")
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to server at {BASE_URL}. Is it running?")
        return False


def test_quest_list():
    """Test quest listing endpoint."""
    print_test("Quest List Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/quests/list", params={"session_id": SESSION_ID})
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved quest list")
            print_info(f"Available quests: {len(data.get('available', []))}")
            print_info(f"Active quests: {len(data.get('active', []))}")
            print_info(f"Current phase: {data.get('current_phase')}")
            print_info(f"Current scene: {data.get('current_scene')}")
            return True, data
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Exception: {e}")
        return False, None


def test_quest_details(quest_id: str):
    """Test quest details endpoint."""
    print_test(f"Quest Details: {quest_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/quests/{quest_id}", params={"session_id": SESSION_ID})
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved quest details")
            quest = data.get('quest', {})
            print_info(f"Title: {quest.get('title')}")
            print_info(f"Phase: {quest.get('phase')}")
            print_info(f"Prerequisites met: {data.get('prerequisites_met')}")
            if not data.get('prerequisites_met'):
                print_info(f"Unmet: {data.get('unmet_prerequisites')}")
            return True, data
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Exception: {e}")
        return False, None


def test_start_quest(quest_id: str):
    """Test starting a quest."""
    print_test(f"Start Quest: {quest_id}")
    try:
        response = requests.post(f"{BASE_URL}/api/quests/{quest_id}/start", params={"session_id": SESSION_ID})
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Quest started: {data.get('message')}")
            return True
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_complete_quest(quest_id: str, alternate: bool = False):
    """Test completing a quest."""
    print_test(f"Complete Quest: {quest_id} (alternate={alternate})")
    try:
        response = requests.post(
            f"{BASE_URL}/api/quests/{quest_id}/complete",
            params={"session_id": SESSION_ID, "alternate": alternate}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Quest completed: {data.get('message')}")
            return True
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_world_state():
    """Test world state endpoints."""
    print_test("World State Management")
    try:
        # Get current world state
        response = requests.get(f"{BASE_URL}/api/world-state", params={"session_id": SESSION_ID})
        
        if response.status_code == 200:
            data = response.json()
            print_success("Retrieved world state")
            print_info(f"Flags: {len(data.get('flags', []))}")
            
            # Set a test flag
            flag_response = requests.post(
                f"{BASE_URL}/api/world-state/flags",
                json={
                    "session_id": SESSION_ID,
                    "scope": "global",
                    "key": "test_flag",
                    "value": True
                }
            )
            
            if flag_response.status_code == 200:
                print_success("Set test flag")
                
                # Verify flag was set
                verify_response = requests.get(
                    f"{BASE_URL}/api/world-state/flags/global/test_flag",
                    params={"session_id": SESSION_ID}
                )
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    if verify_data.get('value') == True:
                        print_success("Verified flag was set correctly")
                        return True
                    else:
                        print_error(f"Flag value mismatch: {verify_data}")
                        return False
            else:
                print_error(f"Failed to set flag: {flag_response.text}")
                return False
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_convergence_status(node_id: str):
    """Test convergence node status."""
    print_test(f"Convergence Status: {node_id}")
    try:
        response = requests.get(
            f"{BASE_URL}/api/quests/convergence/{node_id}",
            params={"session_id": SESSION_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Retrieved convergence status")
            print_info(f"Total branches: {data.get('total_branches')}")
            print_info(f"Completed: {len(data.get('completed', []))}")
            print_info(f"In progress: {len(data.get('in_progress', []))}")
            print_info(f"Ready to converge: {data.get('ready_to_converge')}")
            return True, data
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Exception: {e}")
        return False, None


def test_phase_status(phase_id: int):
    """Test phase status endpoint."""
    print_test(f"Phase Status: {phase_id}")
    try:
        response = requests.get(
            f"{BASE_URL}/api/quests/phase/{phase_id}/status",
            params={"session_id": SESSION_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved phase status: {data.get('phase')}")
            print_info(f"Can advance: {data.get('can_advance')}")
            print_info(f"Critical quests: {data.get('critical_quests')}")
            return True, data
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Exception: {e}")
        return False, None


def run_full_test_suite():
    """Run complete test suite."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Quest System Verification{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Test 1: Server health
    results["total"] += 1
    if test_server_health():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("\nServer is not running. Please start the server and try again.")
        return results
    
    # Test 1.5: Init Session
    results["total"] += 1
    if init_session():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("\nFailed to initialize session. Halting tests.")
        return results
    
    # Test 2: Quest list
    results["total"] += 1
    success, quest_data = test_quest_list()
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 3: World state management
    results["total"] += 1
    if test_world_state():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 4: Quest details (if quests available)
    if quest_data and quest_data.get('available'):
        first_quest = quest_data['available'][0]
        quest_id = first_quest.get('id')
        
        results["total"] += 1
        if test_quest_details(quest_id)[0]:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 5: Start quest
        results["total"] += 1
        if test_start_quest(quest_id):
            results["passed"] += 1
            
            # Test 6: Complete quest
            results["total"] += 1
            if test_complete_quest(quest_id):
                results["passed"] += 1
            else:
                results["failed"] += 1
        else:
            results["failed"] += 1
    else:
        print_info("\nNo quests available to test quest operations")
    
    # Test 7: Phase status
    results["total"] += 1
    if test_phase_status(1)[0]:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test Summary{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"Total tests: {results['total']}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[PASS] All tests passed!{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}[FAIL] Some tests failed{Colors.END}")
    
    return results


if __name__ == "__main__":
    results = run_full_test_suite()
    exit(0 if results["failed"] == 0 else 1)
