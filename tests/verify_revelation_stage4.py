import requests
import json
import os

BASE_URL = "http://localhost:8000/api"
SESSION_ID = "default"

def test_choice_crystallized():
    print("\n--- Testing Choice Crystallized Stage ---")
    
    # 1. Trigger choice crystallized
    print(f"Triggering Stage 4: Choice Crystallized for session {SESSION_ID}...")
    response = requests.post(f"{BASE_URL}/narrative/revelation/choice-crystallized?session_id={SESSION_ID}")
    
    if response.status_code != 200:
        print(f"FAILED: {response.status_code} - {response.text}")
        return
        
    data = response.json()
    print("SUCCESS: Revelation data received")
    print(f"Archetype: {data.get('pattern_name')}")
    print(f"Scene ID: {data.get('scene_id')}")
    
    scene_id = data.get('scene_id')
    wound = data.get('player_wound', 'controller')
    
    # 2. Respond to revelation
    print(f"Responding to Stage 4...")
    payload = {
        "session_id": SESSION_ID,
        "stage": "choice_crystallized",
        "scene_id": scene_id,
        "response_type": "engaged",
        "wound_type": wound
    }
    
    response = requests.post(f"{BASE_URL}/narrative/revelation/respond", json=payload)
    
    if response.status_code != 200:
        print(f"FAILED: {response.status_code} - {response.text}")
        return
        
    data = response.json()
    print(f"SUCCESS: Response recorded. Success: {data.get('success')}")

def test_revelation_check():
    print("\n--- Testing Revelation Check ---")
    response = requests.get(f"{BASE_URL}/narrative/revelation/check?session_id={SESSION_ID}")
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"Pending revelation found: {data.get('stage')}")
        else:
            print("No pending revelation (expected if thresholds not met)")
    else:
        print(f"FAILED: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Ensure server is running or this will fail
    try:
        test_choice_crystallized()
        test_revelation_check()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the server. Is it running?")
