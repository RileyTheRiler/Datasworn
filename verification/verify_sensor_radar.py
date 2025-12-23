#!/usr/bin/env python3
"""
Sensor Radar & POI System Verification Script

Tests the POI (Points of Interest) API endpoints to ensure proper
discovery, location tracking, and quest hook integration.
"""

import requests
import sys
import time

# Configuration
BASE_URL = "http://127.0.0.1:8001/api"
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
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")


def test_poi_nearby():
    """Test fetching nearby POIs."""
    print_test_header("POI Nearby Retrieval")
    
    try:
        # Test from Engine Room location (100, 50)
        response = requests.get(
            f"{BASE_URL}/poi/nearby",
            params={
                "session_id": SESSION_ID,
                "x": 100,
                "y": 50,
                "radius": 500
            },
            timeout=5
        )
        
        if response.status_code != 200:
            print_error(f"Failed with status {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        pois = data.get("pois", [])
        count = data.get("count", 0)
        
        print_success(f"Retrieved {count} POIs")
        
        if count > 0:
            print_info("Sample POI:")
            sample = pois[0]
            print(f"  - ID: {sample.get('id')}")
            print(f"  - Name: {sample.get('name')}")
            print(f"  - Type: {sample.get('poi_type')}")
            print(f"  - Location: {sample.get('location')}")
            print(f"  - Discovered: {sample.get('discovered')}")
        
        return True
        
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_poi_discovery():
    """Test POI discovery mechanism."""
    print_test_header("POI Discovery")
    
    try:
        # Discover at Engine Room location
        response = requests.post(
            f"{BASE_URL}/poi/discover",
            json={
                "session_id": SESSION_ID,
                "x": 100,
                "y": 50
            },
            timeout=5
        )
        
        if response.status_code != 200:
            print_error(f"Failed with status {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        discovered = data.get("discovered", [])
        count = data.get("count", 0)
        
        print_success(f"Discovered {count} new POIs")
        
        if count > 0:
            for poi in discovered:
                print_info(f"Discovered: {poi.get('name')} ({poi.get('poi_type')})")
                print(f"  Description: {poi.get('description')}")
        else:
            print_info("No new POIs discovered (may already be discovered)")
        
        return True
        
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_quest_hooks():
    """Test quest hook retrieval from POIs."""
    print_test_header("Quest Hook Integration")
    
    try:
        response = requests.get(
            f"{BASE_URL}/poi/quest-hooks",
            params={
                "session_id": SESSION_ID,
                "x": 100,
                "y": 50,
                "radius": 500
            },
            timeout=5
        )
        
        if response.status_code != 200:
            print_error(f"Failed with status {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        hooks = data.get("quest_hooks", [])
        count = data.get("count", 0)
        
        print_success(f"Found {count} quest hooks")
        
        if count > 0:
            for hook in hooks:
                print_info(f"Quest Hook: {hook}")
        
        return True
        
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def test_poi_summary():
    """Test POI heatmap summary."""
    print_test_header("POI Heatmap Summary")
    
    try:
        response = requests.get(
            f"{BASE_URL}/poi/summary",
            params={"session_id": SESSION_ID},
            timeout=5
        )
        
        if response.status_code != 200:
            print_error(f"Failed with status {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        
        print_success("Retrieved POI summary")
        print(f"  Total POIs: {data.get('total_pois', 0)}")
        print(f"  Discovered: {data.get('discovered', 0)}")
        print(f"  Undiscovered: {data.get('undiscovered', 0)}")
        print(f"  Current Phase: {data.get('current_phase', 1)}")
        
        by_type = data.get('by_type', {})
        if by_type:
            print_info("POIs by Type:")
            for poi_type, count in by_type.items():
                print(f"    {poi_type}: {count}")
        
        return True
        
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def main():
    print(f"\n{Colors.HEADER}Sensor Radar & POI System Verification{Colors.END}")
    print(f"Target: {BASE_URL}")
    print(f"Session: {SESSION_ID}")
    
    tests = [
        ("POI Nearby", test_poi_nearby),
        ("POI Discovery", test_poi_discovery),
        ("Quest Hooks", test_quest_hooks),
        ("POI Summary", test_poi_summary),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            failed += 1
        time.sleep(0.5)  # Brief pause between tests
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}RESULTS: {passed} Passed, {failed} Failed{Colors.END}")
    print(f"{Colors.HEADER}{'='*60}{Colors.END}\n")
    
    if failed > 0:
        sys.exit(1)
    else:
        print_success("All POI system tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
