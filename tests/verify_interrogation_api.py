"""
Verification script for Interrogation API.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import app, SESSIONS
from src.game_state import create_initial_state

def test_api_flow():
    client = TestClient(app)
    
    # 1. Start Session
    print(">>> Starting Session...")
    resp = client.post("/api/session/start", json={"character_name": "Detective"})
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}")
    
    # 2. Start Interrogation
    print("\n>>> POST /api/narrative/interrogate/start (Torres)")
    resp = client.post("/api/narrative/interrogate/start", json={
        "session_id": session_id,
        "npc_id": "torres"
    })
    
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
        
    assert resp.status_code == 200
    data = resp.json()
    print(f"NPC: {data['npc_text']}")
    print(f"Choices: {len(data['choices'])}")
    
    assert len(data['choices']) > 0
    choice_id = data['choices'][0]['id']
    
    # 3. Respond
    print(f"\n>>> POST /api/narrative/interrogate/respond (Choice: {choice_id})")
    resp = client.post("/api/narrative/interrogate/respond", json={
        "session_id": session_id,
        "choice_id": choice_id
    })
    
    assert resp.status_code == 200
    data = resp.json()
    print(f"NPC Response: {data['npc_text']}")
    print(f"Signals: {data.get('signals')}")
    
    print("\n[SUCCESS] API Flow Verified.")

if __name__ == "__main__":
    try:
        test_api_flow()
    except Exception as e:
        print(f"\n[FAILED] {e}")
        import traceback
        traceback.print_exc()
