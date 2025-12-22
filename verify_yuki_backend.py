import requests
import json
import time

BASE_URL = "http://localhost:8000"
SESSION_ID = f"test_yuki_{int(time.time())}"

def test_yuki_setup():
    print("--- Initializing Session ---")
    init_data = {
        "character_name": "Test Captain",
        "background_vow": "Find the truth about the murder",
        "portrait_style": "realistic"
    }
    resp = requests.post(f"{BASE_URL}/api/session/start", json=init_data)
    if resp.status_code == 200:
        print("Session initialized successfully.")
        return True
    else:
        print(f"Failed to initialize session: {resp.status_code}")
        return False

def test_murder_resolution():
    print("\n--- Testing Murder Resolution Endpoint ---")
    resp = requests.get(f"{BASE_URL}/api/narrative/murder-resolution?session_id=default")
    if resp.status_code == 200:
        data = resp.json()
        wound = data.get('player_wound')
        print(f"Player Wound detected: {wound}")
        
        revelation = data.get('revelation', {})
        phases = revelation.get('phases', [])
        
        # Verify 5 phases
        if len(phases) == 5:
            print("SUCCESS: 5 phases of revelation found.")
        else:
            print(f"WARNING: Expected 5 phases, found {len(phases)}")
            
        # Verify Phase 4 (The Mirror) contains new content
        mirror_phase = next((p for p in phases if p.get('phase_id') == 4), None)
        if mirror_phase:
            dialogue = mirror_phase.get('dialogue', "")
            print(f"Mirror Dialogue Phase 4: {dialogue[:150]}...")
            if "You understand control, don't you?" in dialogue or "You keep your distance too" in dialogue or "You expect betrayal" in dialogue:
                print("SUCCESS: New Mirror Speech content detected in Phase 4.")
            else:
                print("FAILURE: New Mirror Speech content NOT found in Phase 4.")
        
        # Verify Phase 5 (The Question)
        question_phase = next((p for p in phases if p.get('phase_id') == 5), None)
        if question_phase:
            print(f"Final Question: {question_phase.get('question')}")
            
    else:
        print(f"Error fetching murder resolution: {resp.status_code} - {resp.text}")

def verify_yuki_npc_profile():
    print("\n--- Verifying Yuki NPC Profile ---")
    # The ID in RelationshipWeb is 'security'
    resp = requests.get(f"{BASE_URL}/api/npc/security/archetype_response?session_id=default")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Yuki response for archetype ({data.get('player_archetype')}): {data.get('response')}")
    else:
        print(f"Error fetching NPC response: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    if test_yuki_setup():
        test_murder_resolution()
        verify_yuki_npc_profile()
