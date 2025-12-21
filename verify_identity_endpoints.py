"""
Backend Endpoint Verification Script for Character Identity System
Tests all identity-related endpoints before frontend integration.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
session_id = "default"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_get_calibration_scenario():
    print_section("TEST 1: GET /api/calibration/scenario")
    
    response = requests.get(f"{BASE_URL}/api/calibration/scenario")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Scenario Description: {data['description'][:80]}...")
        print(f"✓ Number of Choices: {len(data['choices'])}")
        
        for choice in data['choices']:
            print(f"  - {choice['id']}: {choice['text'][:50]}...")
            print(f"    Impact: {choice['impact']}")
        
        return True
    else:
        print(f"✗ FAILED: {response.text}")
        return False

def test_start_session():
    print_section("TEST 2: POST /api/session/start")
    
    payload = {
        "character_name": "Test Character",
        "background_vow": "Test the identity system",
        "portrait_style": "realistic"
    }
    
    response = requests.post(f"{BASE_URL}/api/session/start", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Session ID: {data['session_id']}")
        print(f"✓ Character Name: {data['state']['character']['name']}")
        return True
    else:
        print(f"✗ FAILED: {response.text}")
        return False

def test_calibrate_choice(choice_id="direct_assault"):
    print_section(f"TEST 3: POST /api/calibrate (choice: {choice_id})")
    
    payload = {
        "session_id": session_id,
        "choice_id": choice_id
    }
    
    response = requests.post(f"{BASE_URL}/api/calibrate", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Archetype: {data['identity']['archetype']}")
        print(f"✓ Violence Score: {data['identity']['scores']['violence']}")
        print(f"✓ Stealth Score: {data['identity']['scores']['stealth']}")
        print(f"✓ Dissonance: {data['identity']['dissonance_score']}")
        print(f"✓ Hint: {data['hint']}")
        
        # Validate archetype matches choice
        if choice_id == "direct_assault":
            expected = "brute"
        elif choice_id == "shadow_slip":
            expected = "shadow"
        else:
            expected = "diplomat"
            
        if data['identity']['archetype'] == expected:
            print(f"✓ Archetype matches expected: {expected}")
            return True
        else:
            print(f"✗ Archetype mismatch! Expected {expected}, got {data['identity']['archetype']}")
            return False
    else:
        print(f"✗ FAILED: {response.text}")
        return False

def test_get_identity():
    print_section("TEST 4: GET /api/identity/{session_id}")
    
    response = requests.get(f"{BASE_URL}/api/identity/{session_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Archetype: {data['archetype']}")
        print(f"✓ Scores: {json.dumps(data['scores'], indent=2)}")
        print(f"✓ Dissonance: {data['dissonance_score']}")
        print(f"✓ Recent Choices: {data['recent_choices']}")
        return True
    else:
        print(f"✗ FAILED: {response.text}")
        return False

def test_get_psyche_with_identity():
    print_section("TEST 5: GET /api/psyche/{session_id} (includes identity)")
    
    response = requests.get(f"{BASE_URL}/api/psyche/{session_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if 'identity' in data:
            print(f"✓ Identity field present in psyche response")
            print(f"✓ Archetype: {data['identity']['archetype']}")
            return True
        else:
            print(f"✗ FAILED: Identity field missing from psyche response")
            return False
    else:
        print(f"✗ FAILED: {response.text}")
        return False

def test_dissonance_via_chat():
    print_section("TEST 6: Dissonance Detection via /api/chat")
    
    # First, get current dissonance
    identity_before = requests.get(f"{BASE_URL}/api/identity/{session_id}").json()
    dissonance_before = identity_before['dissonance_score']
    archetype = identity_before['archetype']
    
    print(f"Current Archetype: {archetype}")
    print(f"Dissonance Before: {dissonance_before}")
    
    # Perform a dissonant action (if Brute, do stealth; if Shadow, do violence)
    if archetype == "brute":
        action = "I quietly sneak past the guards, hiding in the shadows"
    elif archetype == "shadow":
        action = "I charge in with guns blazing, attacking everyone"
    else:
        action = "I brutally attack the diplomat"
    
    print(f"Performing dissonant action: {action}")
    
    payload = {
        "session_id": session_id,
        "action": action
    }
    
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        # Check identity again
        identity_after = requests.get(f"{BASE_URL}/api/identity/{session_id}").json()
        dissonance_after = identity_after['dissonance_score']
        
        print(f"Dissonance After: {dissonance_after}")
        
        if dissonance_after > dissonance_before:
            print(f"✓ Dissonance increased by {dissonance_after - dissonance_before:.3f}")
            return True
        else:
            print(f"✗ FAILED: Dissonance did not increase")
            return False
    else:
        print(f"✗ FAILED: {response.text}")
        return False

def main():
    print("\n" + "="*60)
    print("  CHARACTER IDENTITY SYSTEM - BACKEND VERIFICATION")
    print("="*60)
    print("\nEnsure the backend server is running on http://localhost:8000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    results = []
    
    # Run tests in sequence
    results.append(("Calibration Scenario", test_get_calibration_scenario()))
    results.append(("Start Session", test_start_session()))
    results.append(("Apply Calibration", test_calibrate_choice("direct_assault")))
    results.append(("Get Identity", test_get_identity()))
    results.append(("Psyche with Identity", test_get_psyche_with_identity()))
    results.append(("Dissonance Detection", test_dissonance_via_chat()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend is ready for frontend integration.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED. Fix backend before proceeding to frontend.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server at http://localhost:8000")
        print("Please ensure the server is running with: venv\\Scripts\\python.exe src/server.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
