"""
Manual verification script for /api/npc/{npc_id} endpoint.
Run this to verify the backend NPC endpoint works correctly.
"""
import requests
import json

API_URL = "http://localhost:8000/api"

def test_npc_endpoint():
    """Test the NPC endpoint manually."""
    print("=" * 60)
    print("NPC ENDPOINT VERIFICATION SCRIPT")
    print("=" * 60)
    
    # Step 1: Start a session
    print("\n[1] Starting test session...")
    try:
        response = requests.post(f"{API_URL}/session/start", json={
            "character_name": "TestChar",
            "background_vow": "Test the NPC system"
        })
        response.raise_for_status()
        data = response.json()
        session_id = data["session_id"]
        print(f"✅ Session started: {session_id}")
    except Exception as e:
        print(f"❌ Failed to start session: {e}")
        return False
    
    # Step 2: Test fetching NPC by ID
    print("\n[2] Testing NPC fetch by ID (captain)...")
    try:
        response = requests.get(f"{API_URL}/npc/captain", params={"session_id": session_id})
        response.raise_for_status()
        npc_data = response.json()
        
        print(f"✅ NPC fetched successfully")
        print(f"   Name: {npc_data.get('name')}")
        print(f"   Role: {npc_data.get('role')}")
        print(f"   Trust: {npc_data.get('trust')}")
        print(f"   Suspicion: {npc_data.get('suspicion')}")
        print(f"   Disposition: {npc_data.get('disposition')}")
        print(f"   Image URL: {npc_data.get('image_url')}")
        print(f"   Description: {npc_data.get('description', 'N/A')}")
        
        # Verify required fields
        required_fields = ['name', 'role', 'trust', 'suspicion', 'disposition', 'image_url']
        missing = [f for f in required_fields if f not in npc_data]
        if missing:
            print(f"❌ Missing required fields: {missing}")
            return False
        
    except Exception as e:
        print(f"❌ Failed to fetch NPC: {e}")
        return False
    
    # Step 3: Test fetching by name (case-insensitive)
    print("\n[3] Testing NPC fetch by name (Commander Vasquez)...")
    try:
        response = requests.get(f"{API_URL}/npc/Commander%20Vasquez", params={"session_id": session_id})
        response.raise_for_status()
        npc_data = response.json()
        print(f"✅ NPC fetched by name: {npc_data.get('name')}")
    except Exception as e:
        print(f"❌ Failed to fetch NPC by name: {e}")
        return False
    
    # Step 4: Test case-insensitive lookup
    print("\n[4] Testing case-insensitive lookup (CAPTAIN)...")
    try:
        response = requests.get(f"{API_URL}/npc/CAPTAIN", params={"session_id": session_id})
        response.raise_for_status()
        print(f"✅ Case-insensitive lookup works")
    except Exception as e:
        print(f"❌ Case-insensitive lookup failed: {e}")
        return False
    
    # Step 5: Test 404 for unknown NPC
    print("\n[5] Testing 404 for unknown NPC...")
    try:
        response = requests.get(f"{API_URL}/npc/unknown_character", params={"session_id": session_id})
        if response.status_code == 404:
            print(f"✅ Correctly returns 404 for unknown NPC")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            return False
    except requests.exceptions.HTTPError:
        print(f"✅ Correctly returns 404 for unknown NPC")
    
    # Step 6: Test disposition calculation
    print("\n[6] Testing disposition calculation...")
    try:
        response = requests.get(f"{API_URL}/npc/captain", params={"session_id": session_id})
        response.raise_for_status()
        npc_data = response.json()
        
        disposition = npc_data.get('disposition')
        trust = npc_data.get('trust')
        suspicion = npc_data.get('suspicion')
        
        # Verify disposition logic
        expected_disposition = None
        if trust >= 0.7:
            expected_disposition = "loyal"
        elif trust >= 0.5:
            expected_disposition = "friendly"
        elif trust >= 0.3:
            expected_disposition = "neutral"
        elif suspicion >= 0.6:
            expected_disposition = "hostile"
        else:
            expected_disposition = "suspicious"
        
        if disposition == expected_disposition:
            print(f"✅ Disposition correctly calculated: {disposition}")
        else:
            print(f"❌ Disposition mismatch: got {disposition}, expected {expected_disposition}")
            return False
            
    except Exception as e:
        print(f"❌ Disposition test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    return True

if __name__ == "__main__":
    import sys
    success = test_npc_endpoint()
    sys.exit(0 if success else 1)
