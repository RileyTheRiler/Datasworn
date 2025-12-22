"""
Test script for ending API endpoints.
"""

import requests
import json

API_URL = "http://localhost:8000/api"
SESSION_ID = "default"

def test_ending_endpoints():
    print("=== Testing Ending API Endpoints ===\n")
    
    # Test 1: Get decision prompt
    print("1. Testing GET /api/ending/decision-prompt")
    try:
        response = requests.get(f"{API_URL}/ending/decision-prompt", params={"session_id": SESSION_ID})
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success! Archetype: {data['archetype']}")
            print(f"  Question: {data['question']}")
            print(f"  Options: {list(data['options'].keys())}\n")
        else:
            print(f"✗ Failed with status {response.status_code}: {response.text}\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 2: Submit choice
    print("2. Testing POST /api/ending/submit-choice")
    try:
        response = requests.post(
            f"{API_URL}/ending/submit-choice",
            json={"session_id": SESSION_ID, "choice": "accept"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success! Ending Type: {data['ending_type']}")
            print(f"  Archetype: {data['archetype']}")
            print(f"  Choice: {data['choice']}\n")
        else:
            print(f"✗ Failed with status {response.status_code}: {response.text}\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 3: Get narrative beat
    print("3. Testing GET /api/ending/narrative-beat")
    stages = ["decision", "test", "resolution", "wisdom", "final_scene"]
    
    for stage in stages:
        try:
            response = requests.get(
                f"{API_URL}/ending/narrative-beat",
                params={"session_id": SESSION_ID, "stage": stage}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Stage '{stage}': {len(data['narrative'])} characters")
            else:
                print(f"✗ Stage '{stage}' failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Stage '{stage}' error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_ending_endpoints()
