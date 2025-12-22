"""
Camp API Endpoint Verification Script.

Tests all camp system API endpoints to ensure they work correctly.
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8001"
SESSION_ID = "default"


def test_endpoint(name: str, method: str, url: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> bool:
    """Test a single endpoint."""
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, params=params)
        else:
            print(f"[FAIL] {name}: Unsupported method {method}")
            return False
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] {name}")
            # Print first 100 chars of response
            result_str = json.dumps(result)
            if len(result_str) > 100:
                print(f"   Response: {result_str[:100]}...")
            else:
                print(f"   Response: {result_str}")
            return True
        else:
            print(f"[FAIL] {name}: Status {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] {name}: Exception - {str(e)[:100]}")
        return False


def main():
    """Run all API endpoint tests."""
    print("=" * 80)
    print("CAMP API ENDPOINT VERIFICATION")
    print("=" * 80)
    print(f"Testing against: {BASE_URL}")
    print(f"Session ID: {SESSION_ID}\n")
    
    results = {}
    
    # Initialize Session
    print("\n--- Initializing Session ---")
    results["init"] = test_endpoint(
        "POST /api/session/start",
        "POST",
        f"{BASE_URL}/api/session/start",
        data={"character_name": "TestPlayer", "background_vow": "Test Vow"}
    )
    if not results["init"]:
        print("[WARN] Session initialization failed. Subsequent tests may fail.")

    # Test 1: Camp Layout
    print("\n--- Camp Layout ---")
    results["layout"] = test_endpoint(
        "GET /api/camp/layout",
        "GET",
        f"{BASE_URL}/api/camp/layout"
    )
    
    # Test 2: Camp Routines
    print("\n--- Camp Routines ---")
    results["routines"] = test_endpoint(
        "GET /api/camp/routines",
        "GET",
        f"{BASE_URL}/api/camp/routines",
        params={"session_id": SESSION_ID, "hour": 18, "weather": "clear"}
    )
    
    # Test 3: Proximity Interaction
    print("\n--- Hub Interactions ---")
    results["interact"] = test_endpoint(
        "POST /api/camp/interact",
        "POST",
        f"{BASE_URL}/api/camp/interact",
        data={"npc_id": "torres", "player_location": "common_area"},
        params={"session_id": SESSION_ID}
    )
    
    # Test 4: Advance Interaction
    results["interact_advance"] = test_endpoint(
        "POST /api/camp/interact/{npc_id}/advance",
        "POST",
        f"{BASE_URL}/api/camp/interact/torres/advance",
        params={"session_id": SESSION_ID}
    )
    
    # Test 5: Abort Interaction
    results["interact_abort"] = test_endpoint(
        "POST /api/camp/interact/{npc_id}/abort",
        "POST",
        f"{BASE_URL}/api/camp/interact/torres/abort",
        params={"session_id": SESSION_ID}
    )
    
    # Test 6: Get Arc State
    print("\n--- Camp Arcs ---")
    results["arc_state"] = test_endpoint(
        "GET /api/camp/arcs/{npc_id}",
        "GET",
        f"{BASE_URL}/api/camp/arcs/yuki",
        params={"session_id": SESSION_ID}
    )
    
    # Test 7: Advance Arc
    results["arc_advance"] = test_endpoint(
        "POST /api/camp/arcs/{npc_id}/advance",
        "POST",
        f"{BASE_URL}/api/camp/arcs/yuki/advance",
        data={"flag": "test_flag"},
        params={"session_id": SESSION_ID}
    )
    
    # Test 8: Get Morale Status
    results["morale"] = test_endpoint(
        "GET /api/camp/arcs/morale",
        "GET",
        f"{BASE_URL}/api/camp/arcs/morale",
        params={"session_id": SESSION_ID}
    )
    
    # Test 9: Check Events
    print("\n--- Camp Events ---")
    results["events_check"] = test_endpoint(
        "GET /api/camp/events/check",
        "GET",
        f"{BASE_URL}/api/camp/events/check",
        params={"session_id": SESSION_ID, "hour": 19}
    )
    
    # Test 10: Start Event
    results["events_start"] = test_endpoint(
        "POST /api/camp/events/{event_id}/start",
        "POST",
        f"{BASE_URL}/api/camp/events/evening_meal/start",
        params={"session_id": SESSION_ID}
    )
    
    # Test 11: Advance Event
    results["events_advance"] = test_endpoint(
        "POST /api/camp/events/advance",
        "POST",
        f"{BASE_URL}/api/camp/events/advance",
        params={"session_id": SESSION_ID}
    )
    
    # Test 12: Get Journal
    print("\n--- Camp Journal ---")
    results["journal"] = test_endpoint(
        "GET /api/camp/journal",
        "GET",
        f"{BASE_URL}/api/camp/journal",
        params={"session_id": SESSION_ID, "limit": 5}
    )
    
    # Test 13: Get Journal Narrative
    results["journal_narrative"] = test_endpoint(
        "GET /api/camp/journal/narrative",
        "GET",
        f"{BASE_URL}/api/camp/journal/narrative",
        params={"session_id": SESSION_ID, "days": 7}
    )
    
    # Test 14: Perform Affordance
    print("\n--- Player Affordances ---")
    results["affordance"] = test_endpoint(
        "POST /api/camp/affordance",
        "POST",
        f"{BASE_URL}/api/camp/affordance",
        data={"affordance_type": "sit", "npc_id": "kai", "spot_id": "bench_north"},
        params={"session_id": SESSION_ID}
    )
    
    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "[PASS]" if passed_test else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 80)
    print(f"OVERALL: {passed}/{total} endpoints passed")
    
    if passed == total:
        print("[SUCCESS] ALL API ENDPOINTS WORKING!")
        print("=" * 80)
        return 0
    else:
        print("[WARN] Some endpoints failed - check server logs")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    print("\n[WARN] Make sure the server is running on port 8001!")
    print("   Run: python -m uvicorn src.server:app --port 8001 --reload\n")
    
    # Removed blocking input for automation
    # input("Press Enter to start tests...")
    exit(main())
