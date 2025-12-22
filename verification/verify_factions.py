import requests
import json
import sys
import time

BASE_URL = "http://localhost:8001"

def print_pass(message):
    print(f"[PASS] {message}")

def print_fail(message):
    print(f"[FAIL] {message}")

def verify_factions():
    print("Starting Faction System Verification...")
    
    # 0. Health Check
    print("\n0. Health Check...")
    try:
        resp = requests.get(f"{BASE_URL}/")
        if resp.status_code == 200:
            print_pass("Server is online")
        else:
            print_fail(f"Server returned status {resp.status_code}")
            return
    except Exception as e:
        print_fail(f"Could not connect to server: {e}")
        return

    # 1. Start a Session
    print("\n1. Starting Session...")
    try:
        resp = requests.post(f"{BASE_URL}/api/session/start", json={"character_name": "FactionTester"})
        if resp.status_code != 200:
            print_fail(f"Start Session failed: {resp.status_code} - {resp.text}")
            return
        session_id = resp.json()["session_id"]
        print_pass(f"Session started: {session_id}")
    except Exception as e:
        print_fail(f"Could not start session: {e}")
        return

    # 1.5. Initialize Simulation
    print("\n1.5. Initializing Simulation...")
    try:
        resp = requests.get(f"{BASE_URL}/api/world/status/{session_id}")
        resp.raise_for_status()
        print_pass("Simulation initialized")
    except Exception as e:
        print_fail(f"Could not initialize simulation: {e}")
        return

    # 2. Get Initial Faction Status
    print("\n2. Getting Faction Status...")
    try:
        resp = requests.get(f"{BASE_URL}/api/factions/status/{session_id}")
        resp.raise_for_status()
        data = resp.json()
        factions = data.get("factions", [])
        
        if not factions:
            print_fail("No factions returned")
            return
            
        print_pass(f"Retrieved {len(factions)} factions")
        
        # Verify Iron Syndicate exists
        syndicate = next((f for f in factions if f["id"] == "iron_syndicate"), None)
        if syndicate:
            print_pass("Found Iron Syndicate")
            if syndicate["reputation"] == 0.0 and syndicate["standing"] == "NEUTRAL":
                 print_pass("Initial standing is correct")
            else:
                 print_fail(f"Initial standing incorrect: {syndicate}")
        else:
            print_fail("Iron Syndicate not found")
            
    except Exception as e:
        print_fail(f"Failed to get status: {e}")
        return

    # 3. Modify Reputation
    print("\n3. Modifying Reputation...")
    try:
        target_id = "iron_syndicate"
        change_amount = -15.0 # Should drop to Suspicious
        resp = requests.post(
            f"{BASE_URL}/api/factions/{target_id}/reputation", 
            json={
                "session_id": session_id,
                "reputation_change": change_amount,
                "reason": "Test modification"
            }
        )
        resp.raise_for_status()
        result = resp.json()
        
        if result["new_reputation"] == -15.0 and result["new_standing"] == "HOSTILE":
            print_pass("Reputation modified successfully")
        else:
            print_fail(f"Reputation modification failed: {result}")
            
    except Exception as e:
        print_fail(f"Failed to modify reputation: {e}")
        return

    # 4. Verify Persistence
    print("\n4. Verifying Persistence...")
    try:
        resp = requests.get(f"{BASE_URL}/api/factions/{target_id}/{session_id}")
        resp.raise_for_status()
        data = resp.json()
        
        if data["reputation"] == -15.0:
            print_pass("Reputation persisted correctly")
        else:
            print_fail(f"Persisted reputation incorrect: {data}")
            
    except Exception as e:
        print_fail(f"Failed to verify persistence: {e}")
        return

    # 5. Verify Event Generation
    print("\n5. Verifying Event Generation...")
    try:
        # Give a brief pause for event processing if async, though dispatch is sync here
        time.sleep(3)
        resp = requests.get(f"{BASE_URL}/api/world/simulation/events/{session_id}")
        resp.raise_for_status()
        events = resp.json()
        
        # Look for faction_update
        faction_events = [e for e in events if e.get("type") == "faction_update"]
        if faction_events:
            print_pass(f"Found {len(faction_events)} faction update events")
            latest = faction_events[0]
            print(f"Latest event: {latest['data']['description']}")
        else:
            print_fail("No faction_update events found")
            
    except Exception as e:
        print_fail(f"Failed to verify events: {e}")
        return

    print("\nVerification Complete!")

if __name__ == "__main__":
    verify_factions()
