import requests
import json
import time

BASE_URL = "http://localhost:8000"
SESSION_ID = "test_verification_session"

def print_result(name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {name} {details}")

def run_tests():
    print(f"Starting verification tests against {BASE_URL}...")
    
    # 1. Start a Session
    print("\n1. Initializing Session...")
    try:
        # We need to initialize a session first so it exists in SESSIONS
        init_payload = {
            "character_name": "TestPilot", 
            "background_vow": "Test the system"
        }
        # Using the query param session_id if supported, or relying on default/new
        # The start_session endpoint usually returns a session_id
        response = requests.post(f"{BASE_URL}/api/session/start", json=init_payload)
        
        if response.status_code == 200:
            print_result("Start Session", True)
            data = response.json()
            # If the API returns a session_id, use it. Otherwise Stick to our constant if we forced it.
            if "session_id" in data:
                global SESSION_ID
                SESSION_ID = data["session_id"]
                print(f"   Session initialized with ID: {SESSION_ID}")
            
            print(f"   Session initialized.")
        else:
            print_result("Start Session", False, f"Status: {response.status_code}, Body: {response.text}")
            return # Cannot proceed
            
    except Exception as e:
        print_result("Start Session", False, f"Exception: {str(e)}")
        return

    # 2. Verify Audio State Endpoint
    print("\n2. Verifying Audio State Endpoint...")
    try:
        url = f"{BASE_URL}/api/audio/state/{SESSION_ID}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check structure
            has_ambient = "ambient" in data
            has_music = "music" in data
            
            if has_ambient and has_music:
                print_result("Audio Structure", True)
                
                # Check Ambient fields
                amb = data["ambient"]
                amb_ok = "zone_type" in amb and "tracks" in amb and "volume" in amb
                print_result("Ambient Fields", amb_ok, f"Keys: {list(amb.keys())}")
                
                # Check Music fields
                mus = data["music"]
                mus_ok = "track_id" in mus and "filename" in mus and "volume" in mus
                print_result("Music Fields", mus_ok, f"Keys: {list(mus.keys())}")
                
            else:
                print_result("Audio Structure", False, f"Missing keys. Got: {list(data.keys())}")
        else:
            print_result("Audio Endpoint", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_result("Audio Endpoint", False, f"Exception: {str(e)}")

    # 3. Verify Autosave Status Endpoint
    print("\n3. Verifying Autosave Status Endpoint...")
    try:
        url = f"{BASE_URL}/api/autosave/status/{SESSION_ID}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check structure
            has_last_save = "last_save" in data
            
            if has_last_save:
                print_result("Autosave Structure", True, f"last_save: {data['last_save']}")
            else:
                print_result("Autosave Structure", False, f"Missing last_save key. Got: {list(data.keys())}")
        else:
            print_result("Autosave Endpoint", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_result("Autosave Endpoint", False, f"Exception: {str(e)}")

if __name__ == "__main__":
    try:
        # Check if server is running
        requests.get(f"{BASE_URL}/docs")
        run_tests()
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to {BASE_URL}. Is the server running?")
