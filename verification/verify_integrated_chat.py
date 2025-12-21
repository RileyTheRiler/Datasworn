import requests
import time
import sys
import json

BASE_URL = "http://localhost:8000"

def print_separator(title):
    print(f"\n{'='*20} {title} {'='*20}")

def verify_integration():
    print_separator("INTEGRATION TEST: COGNITIVE CHAT")
    
    # 1. Start Session
    print("[1] Starting Session...")
    res = requests.post(f"{BASE_URL}/api/session/start", json={
        "character_name": "TestPilot",
        "background": "Testing the neural link.",
        "ship_name": "Observer",
        "asset_ids": []
    })
    
    if res.status_code != 200:
        print(f"Failed to start session: {res.text}")
        sys.exit(1)
        
    data = res.json()
    session_id = data['session_id']
    print(f"Session Started: {session_id}")
    
    # 2. Chat with Captain
    print("\n[2] Sending Chat: 'Captain, status report.'")
    chat_payload = {
        "session_id": session_id,
        "action": "I approach the Captain. 'Captain, status report on the cognitive systems.'"
    }
    
    start_time = time.time()
    res = requests.post(f"{BASE_URL}/api/chat", json=chat_payload)
    duration = time.time() - start_time
    
    if res.status_code != 200:
        print(f"Chat failed: {res.text}")
        sys.exit(1)
        
    chat_data = res.json()
    narrative = chat_data['narrative']
    print(f"\n[Narrative Output ({duration:.2f}s)]:\n{narrative[:200]}...")
    
    # 3. Verify Cognitive State Update
    print("\n[3] Inspecting Captain's Mind...")
    # Give async DB writes a moment if needed (though they seem synchronous in current impl)
    time.sleep(1) 
    
    res = requests.get(f"{BASE_URL}/api/cognitive/debug/captain", params={"session_id": session_id})
    
    if res.status_code != 200:
        print(f"Debug failed: {res.text}")
        # Try listing IDs if possible or assume failure
        sys.exit(1)
        
    debug_data = res.json()
    print("\n[Captain's Profile]:")
    print(json.dumps(debug_data.get('profile', 'Missing'), indent=2))
    
    memories = debug_data.get('recent_memories_db', [])
    print(f"\n[Recent Memories found: {len(memories)}]")
    
    found_interaction = False
    for mem in memories:
        print(f" - {mem.get('summary', '')}")
        if "cognitive systems" in mem.get('summary', '').lower():
            found_interaction = True
            
    print_separator("RESULT")
    if found_interaction:
        print("✅ SUCCESS: The Captain remembered the interaction!")
    else:
        print("❌ FAILURE: Interaction not found in memory.")
        print("(Note: This might happen if 'Captain' was not considered active or DB write failed)")

if __name__ == "__main__":
    verify_integration()
