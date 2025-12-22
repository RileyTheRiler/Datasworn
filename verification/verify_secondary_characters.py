
import requests
import json
import sys
import os

# Add parent dir to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uvicorn
import threading
import time
# Import directly to test
try:
    from src.narrative.secondary_characters import get_character_data
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

from src.server import app

# Test port
PORT = 8111
BASE_URL = f"http://127.0.0.1:{PORT}"

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")

def verify_character(name, expectations):
    """
    Verify a character's data against expectations.
    """
    print(f"\n--- Verifying {name.upper()} ---")
    try:
        response = requests.get(f"{BASE_URL}/api/narrative/character/{name}")
        if response.status_code != 200:
            print(f"FAILED: API returned {response.status_code}")
            return False
            
        data = response.json()
        
        # Check basic fields
        for field in ["id", "name", "role", "central_problem_answer", "psychological_wound", "backstory"]:
            if field not in data:
                print(f"FAILED: Missing field '{field}'")
                return False
                
        # Check specific expectations
        for key, value_fragment in expectations.items():
            actual_value = str(data.get(key, ""))
            if value_fragment.lower() not in actual_value.lower():
                print(f"FAILED: Expected '{value_fragment}' in '{key}' but got: {actual_value[:50]}...")
                return False
                
        print(f"SUCCESS: {name} verified.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("FAILED: Could not connect to server.")
        return False
    except Exception as e:
        print(f"FAILED: Exception {e}")
        return False

def main():
    print("--- UNIT TEST: Checking get_character_data directly ---")
    try:
        data = get_character_data("torres")
        if data and data['name'] == "Elena Torres":
            print("UNIT TEST PASSED: 'torres' loaded correctly.")
        else:
            print(f"UNIT TEST FAILED: 'torres' data is {data}")
            sys.exit(1)
    except Exception as e:
        print(f"UNIT TEST EXCEPTION: {e}")
        sys.exit(1)

    print(f"Starting ephemeral server on port {PORT}...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give it a moment to spin up
    print("Waiting for server to start...")
    time.sleep(3)
    
    print("Starting Secondary Character Verification...")
    
    try:
        # 1. TORRES
        torres_expectations = {
            "name": "Elena Torres",
            "psychological_wound": "court-martialed",
            "secret_knowledge": "Yuki coming from the captain's quarters"
        }
        
        # 2. KAI
        kai_expectations = {
            "name": "Kai Nakamura",
            "backstory": "Helix Dynamics",
            "secret_knowledge": "manual override lockout"
        }
        
        # 3. OKONKWO
        okonkwo_expectations = {
            "name": "Sofia Okonkwo",
            "psychological_wound": "impossible choice",
            "secret_knowledge": "terminally ill"
        }
        
        # 4. VASQUEZ
        vasquez_expectations = {
            "name": "Miguel Vasquez",
            "role": "Cargo Master",
            "secret_knowledge": "addiction treatment"
        }
        
        # 5. EMBER
        ember_expectations = {
            "name": "Ember Quinn",
            "role": "Apprentice",
            "secret_knowledge": "Don't make me do this the hard way"
        }
        
        results = [
            verify_character("torres", torres_expectations),
            verify_character("kai", kai_expectations),
            verify_character("okonkwo", okonkwo_expectations),
            verify_character("vasquez", vasquez_expectations),
            verify_character("ember", ember_expectations)
        ]
        
        if all(results):
            print("\nALL CHARACTERS VERIFIED SUCCESSFULLY.")
        else:
            print("\nSOME CHECKS FAILED.")
            sys.exit(1)
            
    finally:
        print("Test complete.")
        # Thread will die with main process due to daemon=True

if __name__ == "__main__":
    main()
