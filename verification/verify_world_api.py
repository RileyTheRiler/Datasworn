"""
Verification script for World Simulation API.
Tests integration of World Simulation with FastAPI server using TestClient.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)

def verify_world_api():
    print("======================================================================")
    print("  WORLD API VERIFICATION")
    print("======================================================================")
    
    # 1. Start Session
    print("\n[TEST] Starting Session...")
    init_data = {
        "character_name": "API Tester",
        "background_vow": "Test the world simulation",
        "portrait_style": "realistic"
    }
    response = client.post("/api/session/start", json=init_data)
    if response.status_code == 200:
        session_id = response.json()["session_id"]
        print(f"[OK] Session started: {session_id}")
    else:
        print(f"[FAIL] Failed to start session: {response.text}")
        return False
        
    # 2. Check Initial Status (should initialize simulation)
    print("\n[TEST] Checking World Status...")
    response = client.get(f"/api/world/status/{session_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Status retrieved")
        print(f"  - Weather: {data['weather']}")
        print(f"  - Congestion: {data['congestion']:.2f}")
        print(f"  - Suspicion: {data['suspicion']}")
    else:
        print(f"[FAIL] Failed to get status: {response.text}")
        return False

    # 3. Debug: Set Weather
    print("\n[TEST] Setting Weather to 'ion_storm'...")
    debug_data = {
        "session_id": session_id,
        "weather_state": "ion_storm"
    }
    response = client.post("/api/world/debug/weather", json=debug_data)
    if response.status_code == 200:
        print(f"[OK] Weather set successfully")
    else:
        print(f"[FAIL] Failed to set weather: {response.text}")
        return False
        
    # Verify weather changed
    response = client.get(f"/api/world/status/{session_id}")
    data = response.json()
    if data['weather'] == 'ion_storm':
        print(f"[OK] Verified weather change: ion_storm")
    else:
        print(f"[FAIL] Weather did not change: {data['weather']}")
        return False

    # 4. Tick Simulation
    print("\n[TEST] Ticking Simulation (10 hours)...")
    tick_data = {
        "session_id": session_id,
        "hours": 10.0
    }
    response = client.post("/api/world/tick", json=tick_data)
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Simulation ticked")
        print(f"  - Events generated: {data['tick_count']}")
    else:
        print(f"[FAIL] Failed to tick simulation: {response.text}")
        return False
        
    # 5. Get Events
    print("\n[TEST] Retrieving Event Log...")
    response = client.get(f"/api/world/simulation/events/{session_id}?limit=5")
    if response.status_code == 200:
        events = response.json()
        print(f"[OK] Events retrieved: {len(events)}")
        for i, event in enumerate(events):
            print(f"  [{i+1}] {event['type']}: {str(event['data'])[:50]}...")
    else:
        print(f"[FAIL] Failed to get events: {response.text}")
        return False

    print("\n======================================================================")
    print("  VERIFICATION COMPLETE: ALL TESTS PASSED")
    print("======================================================================")
    return True

if __name__ == "__main__":
    try:
        if verify_world_api():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
