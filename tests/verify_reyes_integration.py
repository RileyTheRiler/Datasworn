"""
Verification Script for Captain Reyes Backstory Integration.
1. Checks the new journal endpoint.
2. Checks the updated murder resolution content for Reyes-specific details.
3. Checks NPC memories for Reyes related info.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import app, SESSIONS

def test_reyes_integration():
    client = TestClient(app)
    
    print("="*60)
    print("CAPTAIN REYES BACKSTORY INTEGRATION VERIFICATION")
    print("="*60)
    
    # 1. Start Session
    print("\n>>> Starting Session...")
    resp = client.post("/api/session/start", json={"character_name": "Detective"})
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}")
    
    # 2. Test Journal Endpoint
    print("\n>>> GET /api/narrative/reyes/journal")
    resp = client.get(f"/api/narrative/reyes/journal?session_id={session_id}")
    assert resp.status_code == 200
    journal_data = resp.json()
    print(f"Number of Journal Entries: {len(journal_data['entries'])}")
    assert len(journal_data['entries']) == 5
    
    # Check for specific entry content
    found_dying_entry = False
    for entry in journal_data['entries']:
        if entry['id'] == "dying":
            found_dying_entry = True
            print(f"  [Found] {entry['title']}: {entry['content'][:50]}...")
            assert "The crew doesn't know I'm dying" in entry['content']
            assert "Torres" in entry['content']
            assert "Kai" in entry['content']
            assert "Okonkwo" in entry['content']
    assert found_dying_entry
    
    # 3. Test Updated Murder Resolution
    print("\n>>> GET /api/narrative/murder-resolution")
    resp = client.get(f"/api/narrative/murder-resolution?session_id={session_id}")
    assert resp.status_code == 200
    resolution = resp.json()['revelation']
    
    # Check Phase 3 for Reyes specific details
    print("\n>>> Checking Phase 3 (The Complication)...")
    phase3 = next((p for p in resolution['phases'] if p['phase_id'] == 3), None)
    assert phase3 is not None
    print(f"  Narrative Beat: {phase3['narrative_beat'][:100]}...")
    assert "terminal neuro-degenerative condition" in phase3['narrative_beat']
    assert "settling accounts" in phase3['narrative_beat']
    assert "Marcus" in phase3['narrative_beat']
    
    # Check Phase 4 for Archetype Dialogue (default is CONTROLLER)
    print("\n>>> Checking Phase 4 (The Mirror) - CONTROLLER...")
    phase4 = next((p for p in resolution['phases'] if p['phase_id'] == 4), None)
    assert phase4 is not None
    assert "Maria" in phase4['dialogue']
    assert "uncertainty" in phase4['dialogue']
    print(f"  Dialogue: {phase4['dialogue'][:100]}...")
    
    # 4. Check NPC Memories
    print("\n>>> Checking NPC Memories (Known Facts)...")
    for npc_id in ["torres", "kai", "medic"]:
        print(f"\n  Checking {npc_id}...")
        resp = client.get(f"/api/npc/{npc_id}?session_id={session_id}")
        assert resp.status_code == 200
        npc_data = resp.json()
        print(f"    Description: {npc_data['description']}")
        # Some memories might be in Known Facts or just implied by description
        if npc_id == "torres":
            assert "disobeying orders" in npc_data['description']
        if npc_id == "medic":
            assert "She knew he was dying" in npc_data['description'] or "diagnosed him" in npc_data['description']

    print("\n" + "="*60)
    print("CAPTAIN REYES INTEGRATION VERIFICATION PASSED!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_reyes_integration()
    except Exception as e:
        print(f"\n[FAILED] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
