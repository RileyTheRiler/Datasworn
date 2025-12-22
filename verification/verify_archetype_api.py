"""
Verification script for archetype API endpoints.

This script tests:
1. Server is running and responsive
2. POST /api/archetype/observe - Submit behavior observations
3. GET /api/archetype/profile - Retrieve archetype profile
4. GET /api/archetype/needs - Get psychological/moral needs
5. GET /api/archetype/revelation - Get revelation progress
6. POST /api/archetype/test-inference - Test inference engine
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
SESSION_ID = "test_archetype_session"


def test_server_health():
    """Test that server is running."""
    print("=" * 80)
    print("TEST 1: Server Health Check")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Server is online: {data}")
            return True
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Is it running?")
        print("  Start server with: python src/server.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def create_test_session():
    """Create a test session."""
    print("\n" + "=" * 80)
    print("TEST 2: Create Test Session")
    print("=" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/session/start",
            json={
                "character_name": "Test Character",
                "background_vow": "Test the archetype system"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            global SESSION_ID
            SESSION_ID = data.get("session_id", "default")
            print(f"✓ Session created: {SESSION_ID}")
            return True
        else:
            print(f"✗ Failed to create session: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_observe_behavior():
    """Test behavior observation endpoint."""
    print("\n" + "=" * 80)
    print("TEST 3: Observe Behavior")
    print("=" * 80)
    
    try:
        # Test 1: Controller dialogue
        print("\nTest 3.1: Controller dialogue observation")
        response = requests.post(
            f"{BASE_URL}/api/archetype/observe",
            json={
                "session_id": SESSION_ID,
                "behavior_type": "dialogue",
                "description": "Tell me everything. I need to know exactly what happened.",
                "context": "Interrogating a suspect",
                "scene_id": "test_scene_001",
                "npc_involved": "Torres"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Observation recorded")
            print(f"    Signals detected: {data.get('signals_detected', {})}")
            print(f"    Primary archetype: {data.get('primary_archetype')}")
            print(f"    Confidence: {data.get('confidence', 0):.2f}")
        else:
            print(f"  ✗ Failed: {response.status_code}")
            print(f"    Response: {response.text}")
            return False
        
        # Test 2: Ghost action
        print("\nTest 3.2: Ghost action observation")
        response = requests.post(
            f"{BASE_URL}/api/archetype/observe",
            json={
                "session_id": SESSION_ID,
                "behavior_type": "action",
                "description": "Leave the conversation early and disappear",
                "context": "Emotional discussion with crew",
                "scene_id": "test_scene_002"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Observation recorded")
            print(f"    Signals detected: {data.get('signals_detected', {})}")
        else:
            print(f"  ✗ Failed: {response.status_code}")
            return False
        
        # Test 3: Multiple controller observations to build profile
        print("\nTest 3.3: Building controller profile with multiple observations")
        controller_dialogues = [
            "You must follow my orders.",
            "I demand an explanation immediately.",
            "This is unacceptable. Explain yourself.",
        ]
        
        for i, dialogue in enumerate(controller_dialogues):
            response = requests.post(
                f"{BASE_URL}/api/archetype/observe",
                json={
                    "session_id": SESSION_ID,
                    "behavior_type": "dialogue",
                    "description": dialogue,
                    "context": "Scene",
                    "scene_id": f"test_scene_{i+3:03d}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Observation {i+1} recorded")
            else:
                print(f"  ✗ Observation {i+1} failed")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_profile():
    """Test profile retrieval endpoint."""
    print("\n" + "=" * 80)
    print("TEST 4: Get Archetype Profile")
    print("=" * 80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/archetype/profile",
            params={"session_id": SESSION_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Profile retrieved:")
            print(f"  Primary: {data.get('primary')}")
            print(f"  Secondary: {data.get('secondary')}")
            print(f"  Tertiary: {data.get('tertiary')}")
            print(f"  Confidence: {data.get('confidence', 0):.2f}")
            print(f"  Observation count: {data.get('observation_count')}")
            print(f"  Overcontrolled tendency: {data.get('overcontrolled_tendency', 0):.3f}")
            print(f"  Undercontrolled tendency: {data.get('undercontrolled_tendency', 0):.3f}")
            
            # Show top 3 archetypes
            archetypes = data.get('archetypes', {})
            sorted_archetypes = sorted(archetypes.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"\n  Top 3 archetypes:")
            for archetype, weight in sorted_archetypes:
                print(f"    {archetype}: {weight:.3f}")
            
            return True
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_needs():
    """Test needs retrieval endpoint."""
    print("\n" + "=" * 80)
    print("TEST 5: Get Psychological/Moral Needs")
    print("=" * 80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/archetype/needs",
            params={"session_id": SESSION_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Needs retrieved:")
            print(f"\n  Psychological:")
            print(f"    Wound: {data.get('psychological_wound')}")
            print(f"    Need: {data.get('psychological_need')}")
            print(f"    Awareness: {data.get('psychological_awareness', 0):.2f}")
            print(f"    Evidence count: {data.get('psychological_evidence_count')}")
            
            print(f"\n  Moral:")
            print(f"    Corruption: {data.get('moral_corruption')}")
            print(f"    Need: {data.get('moral_need')}")
            print(f"    Awareness: {data.get('moral_awareness', 0):.2f}")
            print(f"    Evidence count: {data.get('moral_evidence_count')}")
            
            print(f"\n  Chain: {data.get('wound_to_corruption_chain')}")
            
            return True
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_revelation():
    """Test revelation progress endpoint."""
    print("\n" + "=" * 80)
    print("TEST 6: Get Revelation Progress")
    print("=" * 80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/archetype/revelation",
            params={"session_id": SESSION_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Revelation progress retrieved:")
            print(f"  Current stage: {data.get('current_stage')}")
            print(f"  Progress: {data.get('progress_percentage', 0):.1f}%")
            print(f"\n  Milestones:")
            print(f"    Mirror moment: {data.get('mirror_moment_delivered')}")
            print(f"    Cost revealed: {data.get('cost_revealed')}")
            print(f"    Origin glimpsed: {data.get('origin_glimpsed')}")
            print(f"    Choice crystallized: {data.get('choice_crystallized')}")
            print(f"    Murder solution: {data.get('murder_solution_delivered')}")
            print(f"    Mirror speech: {data.get('mirror_speech_given')}")
            print(f"    Moral decision: {data.get('moral_decision_made')}")
            
            return True
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_inference_endpoint():
    """Test the inference testing endpoint."""
    print("\n" + "=" * 80)
    print("TEST 7: Test Inference Endpoint")
    print("=" * 80)
    
    try:
        # Test with cynic dialogues
        response = requests.post(
            f"{BASE_URL}/api/archetype/test-inference",
            params={"session_id": SESSION_ID},
            json={
                "dialogue_samples": [
                    "This won't work. It never does.",
                    "Hope is just the first step to disappointment.",
                    "Everyone lies. Why should I believe you?",
                    "We're all doomed anyway.",
                    "Optimism is for fools.",
                ]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Inference test completed:")
            print(f"  Observations processed: {data.get('observations_processed')}")
            
            profile = data.get('profile', {})
            print(f"\n  Resulting profile:")
            print(f"    Primary: {profile.get('primary')}")
            print(f"    Secondary: {profile.get('secondary')}")
            print(f"    Confidence: {profile.get('confidence', 0):.2f}")
            
            needs = data.get('needs', {})
            print(f"\n  Inferred needs:")
            print(f"    Psychological wound: {needs.get('psychological_wound')}")
            print(f"    Moral corruption: {needs.get('moral_corruption')}")
            
            return True
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("ARCHETYPE API VERIFICATION")
    print("=" * 80)
    print("\nNOTE: Server must be running on http://localhost:8000")
    print("      Start with: python src/server.py")
    print()
    
    results = []
    
    # Run tests
    results.append(("Server Health", test_server_health()))
    
    if not results[0][1]:
        print("\n✗ Server is not running. Cannot proceed with tests.")
        return 1
    
    results.append(("Create Session", create_test_session()))
    
    if not results[1][1]:
        print("\n✗ Could not create session. Cannot proceed with tests.")
        return 1
    
    results.append(("Observe Behavior", test_observe_behavior()))
    results.append(("Get Profile", test_get_profile()))
    results.append(("Get Needs", test_get_needs()))
    results.append(("Get Revelation", test_get_revelation()))
    results.append(("Test Inference", test_inference_endpoint()))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        print("\nThe archetype system backend is fully functional and ready for frontend integration.")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
