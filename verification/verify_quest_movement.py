#!/usr/bin/env python3
"""
Quest Content & Player Movement Verification Script

Tests quest loading, player movement API, and integration.
"""

import requests
import sys
import time

# Configuration
BASE_URL = "http://127.0.0.1:8001"
SESSION_ID = "default"

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(test_name):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}TEST: {test_name}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")


def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.END}")


def print_error(message):
    print(f"{Colors.RED}[FAIL] {message}{Colors.END}")


def print_info(message):
    print(f"{Colors.YELLOW}[INFO] {message}{Colors.END}")


def test_player_location():
    """Test getting player location."""
    print_test_header("Player Location Retrieval")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/player/location",
            params={"session_id": SESSION_ID},
            timeout=5
        )
        
        if response.status_code != 200:
            print_error(f"Failed with status {response.status_code}")
            return False
        
        data = response.json()
        print_success(f"Player at ({data['x']}, {data['y']})")
        print_info(f"Nearby POIs: {data.get('nearby_pois', 0)}")
        
        return True
        
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_player_movement():
    """Test player movement."""
    print_test_header("Player Movement")
    
    try:
        # Move to Engine Room
        response = requests.post(
            f"{BASE_URL}/api/player/move",
            json={
                "session_id": SESSION_ID,
                "x": 100,
                "y": 50,
                "validate_distance": True
            },
            timeout=5
        )
        
        if response.status_code != 200:
            print_error(f"Failed with status {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        print_success(f"Moved to ({data['location']['x']}, {data['location']['y']})")
        print_info(f"Distance moved: {data['distance_moved']:.1f} units")
        print_info(f"Nearby POIs: {data.get('nearby_pois', 0)}")
        
        return True
        
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_quest_loading():
    """Test quest system loading."""
    print_test_header("Quest Loading")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/quests/list",
            params={"session_id": SESSION_ID},
            timeout=5
        )
        
        if response.status_code != 200:
            print_error(f"Failed with status {response.status_code}")
            return False
        
        data = response.json()
        available = data.get("available", [])
        active = data.get("active", [])
        
        print_success(f"Quest system operational")
        print_info(f"Available quests: {len(available)}")
        print_info(f"Active quests: {len(active)}")
        
        # Check if our new quests loaded
        quest_ids = [q['id'] for q in available]
        for quest_id in ['help_engineer', 'discover_truth', 'investigate_crew']:
            if quest_id in quest_ids:
                print_success(f"Quest '{quest_id}' loaded successfully")
            else:
                print_info(f"Quest '{quest_id}' not yet available (may require prerequisites)")
        
        return True
        
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_integrated_flow():
    """Test integrated POI discovery -> quest start -> movement flow."""
    print_test_header("Integrated Flow")
    
    try:
        # 1. Move to Engine Room POI
        print_info("Step 1: Moving to Engine Room...")
        move_response = requests.post(
            f"{BASE_URL}/api/player/move",
            json={"session_id": SESSION_ID, "x": 100, "y": 50, "validate_distance": False},
            timeout=5
        )
        
        if move_response.status_code != 200:
            print_error("Movement failed")
            return False
        
        print_success("Moved to Engine Room")
        
        # 2. Discover POI (should auto-start quest)
        print_info("Step 2: Discovering Engine Room POI...")
        discover_response = requests.post(
            f"{BASE_URL}/api/poi/discover",
            json={"session_id": SESSION_ID, "x": 100, "y": 50},
            timeout=5
        )
        
        if discover_response.status_code != 200:
            print_error("Discovery failed")
            return False
        
        discover_data = discover_response.json()
        quests_started = discover_data.get("quests_started", [])
        
        if quests_started:
            print_success(f"Quest auto-started: {quests_started[0]['quest_id']}")
        else:
            print_info("No new quests started (POI may already be discovered)")
        
        # 3. Check active quests
        print_info("Step 3: Checking active quests...")
        quests_response = requests.get(
            f"{BASE_URL}/api/quests/list",
            params={"session_id": SESSION_ID},
            timeout=5
        )
        
        if quests_response.status_code == 200:
            quests_data = quests_response.json()
            active = quests_data.get("active", [])
            if active:
                print_success(f"Active quests: {len(active)}")
                for quest in active:
                    print_info(f"  - {quest.get('title', quest.get('id'))}")
            else:
                print_info("No active quests")
        
        return True
        
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def main():
    print(f"\n{Colors.HEADER}Quest Content & Player Movement Verification{Colors.END}")
    print(f"Target: {BASE_URL}")
    print(f"Session: {SESSION_ID}")
    
    # Initialize session first
    print(f"\n{Colors.YELLOW}Initializing session...{Colors.END}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/session/start",
            json={"character_name": "Test Character"},
            timeout=10
        )
        if response.status_code == 200:
            print(f"{Colors.GREEN}[OK] Session initialized{Colors.END}")
        else:
            print(f"{Colors.YELLOW}[WARN] Session init returned {response.status_code}: {response.text[:100]}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Could not initialize session: {e}{Colors.END}")
        print(f"{Colors.YELLOW}[INFO] Tests may fail without a valid session{Colors.END}")
    
    # Give the server a moment to finish initialization
    time.sleep(1)
    
    tests = [
        ("Player Location", test_player_location),
        ("Player Movement", test_player_movement),
        ("Quest Loading", test_quest_loading),
        ("Integrated Flow", test_integrated_flow),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            failed += 1
        time.sleep(0.5)
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}RESULTS: {passed} Passed, {failed} Failed{Colors.END}")
    print(f"{Colors.HEADER}{'='*60}{Colors.END}\n")
    
    if failed > 0:
        sys.exit(1)
    else:
        print_success("All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
