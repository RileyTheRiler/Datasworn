"""
Quick test script to verify the /api/cognitive/interact endpoint.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_cognitive_endpoint():
    print("=" * 60)
    print("Testing Cognitive Engine Endpoint")
    print("=" * 60)
    
    # 1. Start a session first
    print("\n[1] Starting session...")
    try:
        response = requests.post(f"{BASE_URL}/api/session/start", json={
            "character_name": "TestPlayer",
            "background_vow": "Test the Cognitive Engine"
        })
        if response.status_code == 200:
            print("✓ Session started successfully")
            session_data = response.json()
            session_id = session_data.get("session_id", "default")
        else:
            print(f"✗ Session start failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"✗ Connection error: {e}")
        print("Make sure the server is running: python src/server.py")
        return
    
    # 2. Test cognitive interaction
    print(f"\n[2] Testing /api/cognitive/interact...")
    try:
        response = requests.post(f"{BASE_URL}/api/cognitive/interact", json={
            "session_id": session_id,
            "action": "Greetings, Janus. I seek passage through the gate."
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Cognitive Engine Response:")
            print(f"  Narrative: {data.get('narrative', 'N/A')[:200]}...")
            print(f"  State Updates: {data.get('state_updates', {})}")
        else:
            print(f"✗ Request failed")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 3. Test debug endpoint
    print(f"\n[3] Testing /api/cognitive/debug/janus_01...")
    try:
        response = requests.get(f"{BASE_URL}/api/cognitive/debug/janus_01", params={
            "session_id": session_id
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Debug Data:")
            print(f"  Profile: {data.get('profile', {}).get('name', 'N/A')}")
            print(f"  Memories: {len(data.get('recent_memories', []))} recent")
            print(f"  Relationships: {list(data.get('relationships', {}).keys())}")
        else:
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_cognitive_endpoint()
