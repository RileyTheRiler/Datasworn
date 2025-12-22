"""
Verification Script for the Murder Resolution Endpoint.
Checks that /api/narrative/murder-resolution returns the expected structure.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import app, SESSIONS

def test_murder_resolution_endpoint():
    client = TestClient(app)
    
    print("="*60)
    print("MURDER RESOLUTION ENDPOINT VERIFICATION")
    print("="*60)
    
    # 1. Start Session
    print("\n>>> Starting Session...")
    resp = client.post("/api/session/start", json={"character_name": "Detective"})
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}")
    
    # 2. Get Murder Resolution (Initial state, should be based on default/CONTROLLER)
    print("\n>>> GET /api/narrative/murder-resolution")
    resp = client.get(f"/api/narrative/murder-resolution?session_id={session_id}")
    
    assert resp.status_code == 200
    data = resp.json()
    
    print(f"Player Wound: {data['player_wound']}")
    revelation = data['revelation']
    print(f"Number of Phases: {len(revelation['phases'])}")
    
    for phase in revelation['phases']:
        print(f"  Phase {phase['phase_id']}: {phase['name']}")
        if 'narrative_beat' in phase:
            print(f"    Beat: {phase['narrative_beat'][:60]}...")
        if 'dialogue' in phase:
            print(f"    Dialogue: {phase['dialogue'][:60]}...")
        if 'question' in phase:
            print(f"    Question: {phase['question']}")
            
    # Verify mandatory phases
    phase_names = [p['name'] for p in revelation['phases']]
    assert "The Facts" in phase_names
    assert "The Why" in phase_names
    assert "The Complication" in phase_names
    assert "The Mirror" in phase_names
    assert "The Question" in phase_names
    
    print("\n>>> Meta Analysis")
    print(f"  What Mirror Shows: {revelation['meta_analysis']['what_mirror_shows']}")
    print(f"  Parallel: {revelation['meta_analysis']['parallel']}")

    print("\n" + "="*60)
    print("MURDER RESOLUTION VERIFICATION PASSED!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_murder_resolution_endpoint()
    except Exception as e:
        print(f"\n[FAILED] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
