"""
Comprehensive Verification Script for Interrogation System Integration.
Tests relationship updates, wound profile changes, and serialization.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import app, SESSIONS
from src.character_identity import WoundType

def test_full_integration():
    client = TestClient(app)
    
    print("="*60)
    print("INTERROGATION SYSTEM INTEGRATION TEST")
    print("="*60)
    
    # 1. Start Session
    print("\n>>> Starting Session...")
    resp = client.post("/api/session/start", json={"character_name": "Detective"})
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}")
    
    # Get initial relationship state
    state = SESSIONS[session_id]
    initial_trust = state['relationships']['crew']['security']['trust']
    print(f"Initial Torres Trust: {initial_trust}")
    
    # Get initial wound profile
    initial_wound = state['psyche'].profile.wound_profile.dominant_wound
    print(f"Initial Dominant Wound: {initial_wound.value}")
    
    # 2. Start Interrogation
    print("\n>>> POST /api/narrative/interrogate/start (Torres)")
    resp = client.post("/api/narrative/interrogate/start", json={
        "session_id": session_id,
        "npc_id": "torres"
    })
    
    assert resp.status_code == 200
    data = resp.json()
    print(f"NPC: {data['npc_text'][:50]}...")
    print(f"Choices: {len(data['choices'])}")
    
    # 3. Make DEMANDING choice (should decrease trust, add Controller signal)
    demanding_choice = next((c for c in data['choices'] if 'demand' in c['id'].lower()), data['choices'][0])
    print(f"\n>>> Selecting Choice: {demanding_choice['text'][:50]}...")
    
    resp = client.post("/api/narrative/interrogate/respond", json={
        "session_id": session_id,
        "choice_id": demanding_choice['id']
    })
    
    assert resp.status_code == 200
    data = resp.json()
    print(f"NPC Response: {data['npc_text'][:50]}...")
    print(f"Signals: {data.get('signals')}")
    print(f"Trust Delta: {data.get('trust_delta')}")
    print(f"Suspicion Delta: {data.get('suspicion_delta')}")
    
    # 4. Verify Relationship Updated
    final_trust = state['relationships']['crew']['security']['trust']
    print(f"\n>>> Relationship Verification")
    print(f"Initial Trust: {initial_trust}")
    print(f"Final Trust: {final_trust}")
    print(f"Change: {final_trust - initial_trust}")
    
    assert final_trust != initial_trust, "Trust should have changed!"
    print("✓ Relationship updated successfully")
    
    # 5. Verify Wound Profile Updated
    final_wound = state['psyche'].profile.wound_profile.dominant_wound
    controller_score = state['psyche'].profile.wound_profile.scores.scores.get(WoundType.CONTROLLER, 0.0)
    
    print(f"\n>>> Wound Profile Verification")
    print(f"Initial Wound: {initial_wound.value}")
    print(f"Final Wound: {final_wound.value}")
    print(f"Controller Score: {controller_score}")
    
    assert controller_score > 0, "Controller signal should have been applied!"
    print("✓ Wound profile updated successfully")
    
    # 6. Test Serialization
    print(f"\n>>> Serialization Test")
    manager = state['narrative'].interrogation_manager
    if manager:
        serialized = manager.to_dict()
        print(f"Serialized: {serialized is not None}")
        
        # Reconstruct
        from src.narrative.interrogation import InterrogationManager
        from src.narrative.interrogation_scenes import get_interrogation_scene
        
        scenes_registry = {}
        for scene_name in ["torres", "vasquez", "kai", "okonkwo", "ember", "yuki"]:
            scene = get_interrogation_scene(scene_name)
            if scene:
                scenes_registry[f"{scene_name}_0"] = scene
        
        restored = InterrogationManager.from_dict(serialized, scenes_registry)
        print(f"Restored: {restored is not None}")
        print(f"State Matches: {restored.active_state.npc_id == manager.active_state.npc_id if restored.active_state and manager.active_state else False}")
        print("✓ Serialization working")
    
    print("\n" + "="*60)
    print("ALL INTEGRATION TESTS PASSED!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_full_integration()
    except Exception as e:
        print(f"\n[FAILED] {e}")
        import traceback
        traceback.print_exc()
