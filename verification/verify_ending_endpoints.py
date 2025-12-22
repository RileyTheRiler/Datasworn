import requests
import json
import sys

BASE_URL = "http://localhost:8001"
SESSION_ID = "default"

def test_endpoint(method, path, data=None, params=None, timeout=30):
    url = f"{BASE_URL}{path}"
    print(f"\n--- Testing {method} {path} ---")
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            # Print a snippet of the response
            content = response.json()
            print(json.dumps(content, indent=2)[:500] + "...")
            return content
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def main():
    # 1. Initialize session
    print("Pre-requisite: ensure server is running at", BASE_URL)
    
    init_data = {
        "character_name": "Test Detective",
        "background": "A gritty detective running from their past.",
        "portrait_style": "realistic"
    }
    session = test_endpoint("POST", "/api/session/start", data=init_data, timeout=120)
    if not session:
        print("Failed to start session. Aborting.")
        return

    # 2. Get Ending Sequence
    sequence = test_endpoint("GET", "/api/narrative/ending/sequence", params={"session_id": SESSION_ID})
    if not sequence:
        print("Failed to get ending sequence. Aborting.")
        return

    # 3. Submit Ending Decision
    # Let's try "accept" (Hero path)
    decision_data = {
        "session_id": SESSION_ID,
        "choice": "accept"
    }
    decision = test_endpoint("POST", "/api/narrative/ending/decision", data=decision_data)
    if not decision:
        print("Failed to submit ending decision.")
    
    # 4. Get Ending Progress (Stage: Test)
    progress = test_endpoint("GET", "/api/narrative/ending/progress", params={"session_id": SESSION_ID, "stage": "test"})
    if not progress:
        print("Failed to get ending progress.")

    # 5. Get Ending Progress (Stage: Resolution)
    progress_res = test_endpoint("GET", "/api/narrative/ending/progress", params={"session_id": SESSION_ID, "stage": "resolution"})
    
    # 6. Check Narrative Premise endpoint (just in case)
    test_endpoint("GET", "/api/narrative/premise")

if __name__ == "__main__":
    main()
