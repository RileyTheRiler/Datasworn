"""
Quest System Verification Script

Comprehensive testing of the threaded quest architecture backend.
Tests all components before frontend integration.
"""

import requests
import json
from typing import Dict, Any

# Base URL for API
BASE_URL = "http://localhost:8001"

class Colors:
    """Terminal colors for output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str):
    """Print test name."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}[OK] {message}{Colors.END}")

def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}[ERR] {message}{Colors.END}")

def print_info(message: str):
    """Print info message."""
    print(f"{Colors.YELLOW}[INFO] {message}{Colors.END}")

def test_quest_list():
    """Test GET /api/quests/list"""
    print_test("Quest List")
    
    try:
        response = requests.get(f"{BASE_URL}/api/quests/list", params={"session_id": "test"})
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Current Phase: {data.get('current_phase')}")
        print_info(f"Current Scene: {data.get('current_scene')}")
        print_info(f"Available Quests: {len(data.get('available', []))}")
        print_info(f"Active Quests: {len(data.get('active', []))}")
        
        if 'available' in data:
            for quest in data['available']:
                print_info(f"  - {quest.get('title')} (ID: {quest.get('id')})")
        
        print_success("Quest list endpoint working")
        return True
    except Exception as e:
        print_error(f"Quest list failed: {e}")
        return False

def test_quest_details():
    """Test GET /api/quests/{quest_id}"""
    print_test("Quest Details")
    
    quest_id = "discover_truth"
    
    try:
        response = requests.get(f"{BASE_URL}/api/quests/{quest_id}", params={"session_id": "test"})
        response.raise_for_status()
        data = response.json()
        
        quest = data.get('quest', {})
        print_info(f"Quest: {quest.get('title')}")
        print_info(f"Description: {quest.get('description')}")
        print_info(f"Type: {quest.get('quest_type')}")
        print_info(f"Phase: {quest.get('phase')}")
        print_info(f"Prerequisites Met: {data.get('prerequisites_met')}")
        
        if not data.get('prerequisites_met'):
            print_info(f"Unmet Prerequisites: {data.get('unmet_prerequisites')}")
        
        print_success("Quest details endpoint working")
        return True
    except Exception as e:
        print_error(f"Quest details failed: {e}")
        return False

def test_quest_start():
    """Test POST /api/quests/{quest_id}/start"""
    print_test("Start Quest")
    
    quest_id = "discover_truth"
    
    try:
        response = requests.post(f"{BASE_URL}/api/quests/{quest_id}/start", params={"session_id": "test"})
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Success: {data.get('success')}")
        print_info(f"Message: {data.get('message')}")
        
        print_success("Quest start endpoint working")
        return True
    except Exception as e:
        print_error(f"Quest start failed: {e}")
        return False

def test_quest_complete():
    """Test POST /api/quests/{quest_id}/complete"""
    print_test("Complete Quest")
    
    quest_id = "discover_truth"
    
    try:
        response = requests.post(f"{BASE_URL}/api/quests/{quest_id}/complete", params={"session_id": "test"})
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Success: {data.get('success')}")
        print_info(f"Message: {data.get('message')}")
        
        print_success("Quest complete endpoint working")
        return True
    except Exception as e:
        print_error(f"Quest complete failed: {e}")
        return False

def test_convergence_status():
    """Test GET /api/quests/convergence/{node_id}"""
    print_test("Convergence Status")
    
    node_id = "discover_truth"
    
    try:
        response = requests.get(f"{BASE_URL}/api/quests/convergence/{node_id}", params={"session_id": "test"})
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Convergence Node: {data.get('convergence_node')}")
        print_info(f"Total Branches: {data.get('total_branches')}")
        print_info(f"Completed: {len(data.get('completed', []))}")
        print_info(f"In Progress: {len(data.get('in_progress', []))}")
        print_info(f"Ready to Converge: {data.get('ready_to_converge')}")
        
        print_success("Convergence status endpoint working")
        return True
    except Exception as e:
        print_error(f"Convergence status failed: {e}")
        return False

def test_phase_status():
    """Test GET /api/quests/phase/{phase_id}/status"""
    print_test("Phase Status")
    
    phase_id = 1
    
    try:
        response = requests.get(f"{BASE_URL}/api/quests/phase/{phase_id}/status", params={"session_id": "test"})
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Phase: {data.get('phase')}")
        print_info(f"Can Advance: {data.get('can_advance')}")
        print_info(f"Critical Quests: {data.get('critical_quests')}")
        
        print_success("Phase status endpoint working")
        return True
    except Exception as e:
        print_error(f"Phase status failed: {e}")
        return False

def test_world_state():
    """Test GET /api/world-state"""
    print_test("World State")
    
    try:
        response = requests.get(f"{BASE_URL}/api/world-state", params={"session_id": "test"})
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Flags: {data.get('flags', [])}")
        print_info(f"Metadata Keys: {list(data.get('metadata', {}).keys())}")
        
        print_success("World state endpoint working")
        return True
    except Exception as e:
        print_error(f"World state failed: {e}")
        return False

def test_set_world_flag():
    """Test POST /api/world-state/flags"""
    print_test("Set World Flag")
    
    try:
        payload = {
            "session_id": "test",
            "scope": "quest",
            "key": "test_flag",
            "value": True
        }
        response = requests.post(f"{BASE_URL}/api/world-state/flags", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Success: {data.get('success')}")
        
        # Verify flag was set
        response2 = requests.get(f"{BASE_URL}/api/world-state/flags/quest/test_flag", params={"session_id": "test"})
        response2.raise_for_status()
        data2 = response2.json()
        
        print_info(f"Flag Value: {data2.get('value')}")
        print_info(f"Flag Type: {data2.get('type')}")
        
        print_success("Set world flag endpoint working")
        return True
    except Exception as e:
        print_error(f"Set world flag failed: {e}")
        return False

def test_poi_nearby():
    """Test GET /api/poi/nearby"""
    print_test("Nearby POIs")
    
    try:
        params = {
            "session_id": "test",
            "x": 100,
            "y": 50,
            "radius": 100
        }
        response = requests.get(f"{BASE_URL}/api/poi/nearby", params=params)
        response.raise_for_status()
        data = response.json()
        
        print_info(f"POIs Found: {data.get('count')}")
        
        for poi in data.get('pois', []):
            print_info(f"  - {poi.get('name')} ({poi.get('poi_type')}) at {poi.get('location')}")
        
        print_success("Nearby POIs endpoint working")
        return True
    except Exception as e:
        print_error(f"Nearby POIs failed: {e}")
        return False

def test_poi_discover():
    """Test POST /api/poi/discover"""
    print_test("Discover POIs")
    
    try:
        params = {
            "session_id": "test",
            "x": 100,
            "y": 50
        }
        response = requests.post(f"{BASE_URL}/api/poi/discover", params=params)
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Newly Discovered: {data.get('count')}")
        
        for poi in data.get('discovered', []):
            print_info(f"  - {poi.get('name')}")
        
        print_success("Discover POIs endpoint working")
        return True
    except Exception as e:
        print_error(f"Discover POIs failed: {e}")
        return False

def test_poi_quest_hooks():
    """Test GET /api/poi/quest-hooks"""
    print_test("POI Quest Hooks")
    
    try:
        params = {
            "session_id": "test",
            "x": 100,
            "y": 50,
            "radius": 100
        }
        response = requests.get(f"{BASE_URL}/api/poi/quest-hooks", params=params)
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Quest Hooks Found: {data.get('count')}")
        print_info(f"Quest IDs: {data.get('quest_hooks')}")
        
        print_success("POI quest hooks endpoint working")
        return True
    except Exception as e:
        print_error(f"POI quest hooks failed: {e}")
        return False

def test_poi_summary():
    """Test GET /api/poi/summary"""
    print_test("POI Summary")
    
    try:
        response = requests.get(f"{BASE_URL}/api/poi/summary", params={"session_id": "test"})
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Total POIs: {data.get('total_pois')}")
        print_info(f"Discovered: {data.get('discovered')}")
        print_info(f"Undiscovered: {data.get('undiscovered')}")
        print_info(f"Current Phase: {data.get('current_phase')}")
        print_info(f"By Phase: {data.get('by_phase')}")
        print_info(f"By Type: {data.get('by_type')}")
        
        print_success("POI summary endpoint working")
        return True
    except Exception as e:
        if 'response' in locals() and hasattr(response, 'text'):
            print_info(f"Response Body: {response.text}")
        print_error(f"POI summary failed: {e}")
        return False

def run_all_tests():
    """Run all verification tests."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}QUEST SYSTEM VERIFICATION{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    tests = [
        ("Quest List", test_quest_list),
        ("Quest Details", test_quest_details),
        ("Start Quest", test_quest_start),
        ("Complete Quest", test_quest_complete),
        ("Convergence Status", test_convergence_status),
        ("Phase Status", test_phase_status),
        ("World State", test_world_state),
        ("Set World Flag", test_set_world_flag),
        ("Nearby POIs", test_poi_nearby),
        ("Discover POIs", test_poi_discover),
        ("POI Quest Hooks", test_poi_quest_hooks),
        ("POI Summary", test_poi_summary),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{status} - {name}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}ALL TESTS PASSED! Backend is ready for frontend integration.{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        return True
    else:
        print(f"\n{Colors.RED}{'='*60}{Colors.END}")
        print(f"{Colors.RED}SOME TESTS FAILED. Fix issues before frontend work.{Colors.END}")
        print(f"{Colors.RED}{'='*60}{Colors.END}\n")
        return False

if __name__ == "__main__":
    import sys
    
    print_info("Checking if server is running...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print_success(f"Server is online: {response.json()}")
    except Exception as e:
        print_error(f"Server is not running at {BASE_URL}")
        print_error("Please start the server with: python -m uvicorn src.server:app --port 8001 --reload")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
