import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def run_test():
    print("Testing Calibration API...")
    
    # 1. Get Scenarios
    try:
        res = requests.get(f"{BASE_URL}/calibration/scenario")
        if res.status_code != 200:
            print(f"FAILED: Get scenarios returned {res.status_code}")
            return False
            
        scenarios = res.json()
        print(f"Received {len(scenarios)} scenarios.")
        
        if not isinstance(scenarios, list):
            print("FAILED: Response is not a list")
            return False
            
        if len(scenarios) < 2:
            print("FAILED: Expected multiple scenarios")
            return False
            
        print("✓ Scenarios retrieval passed")
        
        # Verify specific new scenario exists
        has_coffee = any(s for s in scenarios if "synthesized_caffeine" in str(s)) # rudimentary check
        # Checking by description or text might be safer or just trusting the count for now.
        # But wait, CALIBRATION_SCENARIOS keys are not in the response directly, just values.
        # So I check for text.
        
        coffee_scenario = next((s for s in scenarios if "coffee" in s['description'].lower() or "fabricator" in s['description'].lower()), None)
        if not coffee_scenario:
             print("FAILED: Could not find coffee scenario")
             return False
        print("✓ New content verification passed")

    except Exception as e:
        print(f"FAILED: Exception during get scenarios: {e}")
        return False

    # 2. Test Calibration Submission
    # We need a session ID first.
    try:
        # Start a quick session
        start_res = requests.post(f"{BASE_URL}/session/start", json={"character_name": "TestSubject"})
        if start_res.status_code != 200:
             print("FAILED: Could not start session")
             return False
        session_id = start_res.json()['session_id']
        
        # Submit choice for coffee
        # Find choice id
        coffee_choice_id = coffee_scenario['choices'][0]['id'] # "prioritize_coffee"
        
        cal_res = requests.post(f"{BASE_URL}/calibrate", json={
            "session_id": session_id,
            "choice_id": coffee_choice_id
        })
        
        if cal_res.status_code != 200:
            print(f"FAILED: Calibration submission failed: {cal_res.text}")
            return False
            
        result = cal_res.json()
        print(f"Calibration Result: {result}")
        print("✓ Calibration submission passed")
        
    except Exception as e:
        print(f"FAILED: Exception during submission: {e}")
        return False
        
    return True

if __name__ == "__main__":
    if run_test():
        print("ALL TESTS PASSED")
        sys.exit(0)
    else:
        sys.exit(1)
