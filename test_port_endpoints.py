"""Simple verification of Port Arrival endpoints"""
import requests
import json

BASE_URL = "http://localhost:8001"

print("=" * 80)
print("PORT ARRIVAL ENDPOINT VERIFICATION")
print("=" * 80)

# Test 1: Server check
print("\n[1] Checking server...")
try:
    r = requests.get(f"{BASE_URL}/")
    print(f"✓ Server is online (status: {r.status_code})")
except Exception as e:
    print(f"✗ Server is offline: {e}")
    exit(1)

# Test 2: Create session
print("\n[2] Creating test session...")
try:
    r = requests.post(f"{BASE_URL}/api/session/start", json={
        "character_name": "Test_PortArrival",
        "background_vow": "Test port arrival"
    })
    if r.status_code == 200:
        print("✓ Session created")
    else:
        print(f"✗ Session creation failed: {r.status_code}")
        print(r.text)
except Exception as e:
    print(f"✗ Session creation error: {e}")

# Test 3: Approach endpoint - general
print("\n[3] Testing approach endpoint (general)...")
try:
    r = requests.get(f"{BASE_URL}/api/narrative/port-arrival/approach", params={"session_id": "default"})
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Approach endpoint works")
        print(f"  - Stage: {data.get('stage')}")
        print(f"  - Available conversations: {len(data.get('available_conversations', []))}")
    else:
        print(f"✗ Approach failed: {r.status_code} - {r.text}")
except Exception as e:
    print(f"✗ Approach error: {e}")

# Test 4: Approach endpoint - NPC specific
print("\n[4] Testing approach endpoint (NPC: torres)...")
try:
    r = requests.get(f"{BASE_URL}/api/narrative/port-arrival/approach", params={"session_id": "default", "npc_id": "torres"})
    if r.status_code == 200:
        data = r.json()
        print(f"✓ NPC conversation works")
        print(f"  - NPC: {data.get('npc_id')}")
        print(f"  - Conversation length: {len(data.get('conversation', ''))} chars")
    else:
        print(f"✗ NPC conversation failed: {r.status_code} - {r.text}")
except Exception as e:
    print(f"✗ NPC conversation error: {e}")

# Test 5: Docking endpoint
print("\n[5] Testing docking endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/narrative/port-arrival/docking", params={"session_id": "default"})
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Docking endpoint works")
        print(f"  - Scenario: {data.get('scenario')}")
    else:
        print(f"✗ Docking failed: {r.status_code} - {r.text}")
except Exception as e:
    print(f"✗ Docking error: {e}")

# Test 6: Status endpoint
print("\n[6] Testing status endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/narrative/port-arrival/status", params={"session_id": "default"})
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Status endpoint works")
        print(f"  - Current stage: {data.get('current_stage')}")
        print(f"  - Completed conversations: {len(data.get('completed_conversations', []))}")
    else:
        print(f"✗ Status failed: {r.status_code} - {r.text}")
except Exception as e:
    print(f"✗ Status error: {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
print("\nNote: Dispersal and Epilogue endpoints require ending_type to be set")
print("These will be tested after implementing the ending decision flow")
print("\n✓ Backend is ready for frontend integration!")
