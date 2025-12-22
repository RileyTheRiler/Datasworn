"""
Simple test to isolate the archetype API issue.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test 1: Health check
print("Test 1: Health check")
try:
    r = requests.get(f"{BASE_URL}/")
    print(f"✓ Server online: {r.json()}")
except Exception as e:
    print(f"✗ Server error: {e}")
    exit(1)

# Test 2: Create session
print("\nTest 2: Create session")
try:
    r = requests.post(
        f"{BASE_URL}/api/session/start",
        json={"character_name": "Test", "background_vow": "Test"}
    )
    session_id = r.json().get("session_id", "default")
    print(f"✓ Session created: {session_id}")
except Exception as e:
    print(f"✗ Session error: {e}")
    print(f"   Response: {r.text if 'r' in locals() else 'No response'}")
    exit(1)

# Test 3: Observe behavior
print("\nTest 3: Observe behavior")
try:
    r = requests.post(
        f"{BASE_URL}/api/archetype/observe",
        json={
            "session_id": session_id,
            "behavior_type": "dialogue",
            "description": "Tell me everything now.",
            "context": "Test",
            "scene_id": "test_001"
        }
    )
    print(f"✓ Observation recorded: {r.json()}")
except Exception as e:
    print(f"✗ Observation error: {e}")
    print(f"   Status: {r.status_code if 'r' in locals() else 'No response'}")
    print(f"   Response: {r.text if 'r' in locals() else 'No response'}")
    exit(1)

# Test 4: Get profile
print("\nTest 4: Get profile")
try:
    r = requests.get(
        f"{BASE_URL}/api/archetype/profile",
        params={"session_id": session_id}
    )
    profile = r.json()
    print(f"✓ Profile retrieved:")
    print(f"   Primary: {profile.get('primary')}")
    print(f"   Confidence: {profile.get('confidence')}")
except Exception as e:
    print(f"✗ Profile error: {e}")
    print(f"   Status: {r.status_code if 'r' in locals() else 'No response'}")
    print(f"   Response: {r.text if 'r' in locals() else 'No response'}")
    exit(1)

print("\n✓ All basic tests passed!")
