
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import app, SESSIONS, InitRequest
from src.game_state import create_initial_state

async def verify_npc_images():
    print("Verifying NPC Portrait Generation...")
    
    # 1. Initialize State
    session_id = "test_verification_session"
    state = create_initial_state("Test Captain")
    
    # Add a dummy world NPC
    test_npc = {
        "name": "Trader Joe",
        "id": "trader_joe",
        "role": "Merchant",
        "description": "A weary trader with cybernetic eyes.",
        "location": "The Hub",
        "trust": 0.5,
        "suspicion": 0.2
    }
    state['world'].npcs.append(test_npc)
    SESSIONS[session_id] = state
    print("[OK] Session initialized with World NPC.")

    # 2. Test Single Fetch (Lazy Generation)
    print(f"Fetching NPC: {test_npc['name']}...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # We use sync client for testing, but the endpoint is async. 
    # TestClient handles this mostly, but since we are mocking/using internal state, 
    # we need to ensure the event loop is running if we were calling functions directly.
    # However, for TestClient, it should work fine.
    
    # Note: image generation calls external APIs (or mocks). 
    # If no API key, it might return None or placeholder. 
    # We should check if image_url is populated.
    
    response = client.get(f"/api/npc/{test_npc['name']}?session_id={session_id}")
    
    if response.status_code != 200:
        print(f"[FAIL] Fetch failed: {response.status_code} {response.text}")
        return
    
    data = response.json()
    print(f"[OK] Response received: {data.get('name')}")
    
    image_url = data.get('image_url')
    print(f"Image URL: {image_url}")
    
    if image_url and ("/assets/generated/" in image_url or "placeholder" in image_url):
         print(f"[OK] Image URL present: {image_url}")
    else:
         print(f"[WARN] Image URL unexpected format or missing: {image_url}")

    # Check state update
    updated_npc = next(n for n in state['world'].npcs if n['name'] == test_npc['name'])
    if updated_npc.get('image_url') == image_url:
        print("[OK] State updated with image URL.")
    else:
        print("[FAIL] State NOT updated with image URL.")

    # 3. Test Generate All
    # Add another NPC without image
    test_npc_2 = {
        "name": "Pirate Pete",
        "role": "Pirate",
        "description": "Fierce looking pirate."
    }
    state['world'].npcs.append(test_npc_2)
    
    print("Testing Batch Generation...")
    resp_batch = client.post(f"/api/npc/generate-all?session_id={session_id}")
    if resp_batch.status_code == 200:
        print(f"[OK] Batch success: {resp_batch.json()}")
    else:
        print(f"[FAIL] Batch failed: {resp_batch.status_code}")

if __name__ == "__main__":
    asyncio.run(verify_npc_images())
