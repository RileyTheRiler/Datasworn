"""
Test NPC Scheduling API Endpoints

Tests all scheduling, dialogue, and world memory endpoints with the running server.
"""

import requests
import json

BASE_URL = "http://localhost:8001"


def test_schedule_endpoints():
    """Test schedule management endpoints"""
    print("\n=== Testing Schedule Endpoints ===")
    
    # Test 1: Assign schedule
    print("\n1. Assigning farmer schedule...")
    response = requests.post(f"{BASE_URL}/api/npc/schedule/assign", json={
        "npc_id": "test_farmer",
        "archetype": "farmer",
        "region": "default"
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Schedule assigned: {data['archetype']}")
        print(f"   ✓ Tasks: {len(data['schedule']['tasks'])}")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 2: Get schedule
    print("\n2. Getting NPC schedule...")
    response = requests.get(f"{BASE_URL}/api/npc/schedule/test_farmer")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ NPC: {data['npc_id']}")
        print(f"   ✓ Current task: {data.get('current_task', {}).get('behavior', 'None')}")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 3: Get all active schedules
    print("\n3. Getting all active schedules...")
    response = requests.get(f"{BASE_URL}/api/npc/schedules/active")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Active schedules: {data['count']}")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 4: Interrupt schedule
    print("\n4. Interrupting schedule...")
    response = requests.post(f"{BASE_URL}/api/npc/schedule/interrupt", json={
        "npc_id": "test_farmer",
        "reason": "test_alarm",
        "priority": 9,
        "behavior": "flee",
        "duration": 5
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Interrupted: {data['success']}")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 5: Resume schedule
    print("\n5. Resuming schedule...")
    response = requests.post(f"{BASE_URL}/api/npc/schedule/resume/test_farmer")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Resumed: {data['success']}")
    else:
        print(f"   ✗ Error: {response.text}")


def test_dialogue_endpoints():
    """Test dialogue selection endpoints"""
    print("\n=== Testing Dialogue Endpoints ===")
    
    # Test 1: Select dialogue
    print("\n1. Selecting contextual dialogue...")
    response = requests.post(f"{BASE_URL}/api/dialogue/select", json={
        "npc_id": "test_npc",
        "interaction_type": "greeting",
        "context": {
            "player_has_weapon_drawn": True,
            "player_honor": 0.3
        }
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"   ✓ Dialogue: \"{data['text']}\"")
            if data.get('animation'):
                print(f"   ✓ Animation: {data['animation']}")
        else:
            print(f"   ⚠ No matching dialogue")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 2: Get greeting
    print("\n2. Getting NPC greeting...")
    response = requests.get(f"{BASE_URL}/api/dialogue/test_npc/greeting?session_id=default")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Greeting: \"{data['text']}\"")
    else:
        print(f"   ✗ Error: {response.text}")


def test_world_memory_endpoints():
    """Test world memory endpoints"""
    print("\n=== Testing World Memory Endpoints ===")
    
    # Test 1: Record event
    print("\n1. Recording world event...")
    response = requests.post(f"{BASE_URL}/api/world/memory/event", json={
        "area_id": "test_town",
        "event_type": "crime_theft",
        "description": "Someone stole from the market",
        "actor": "player",
        "witnesses": ["npc_1", "npc_2"],
        "severity": 0.6
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Event recorded: {data['event']['event_id']}")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 2: Get area memory
    print("\n2. Getting area memory...")
    response = requests.get(f"{BASE_URL}/api/world/memory/test_town?limit=5")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Rumors: {len(data['rumors'])}")
        for rumor in data['rumors']:
            print(f"      • {rumor}")
        print(f"   ✓ Recent events: {len(data['recent_events'])}")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 3: Get world memory status
    print("\n3. Getting world memory status...")
    response = requests.get(f"{BASE_URL}/api/world/memory/status")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Total areas: {data['total_areas']}")
        print(f"   ✓ Total events: {data['total_events']}")
    else:
        print(f"   ✗ Error: {response.text}")


def test_navigation_endpoints():
    """Test navigation endpoints"""
    print("\n=== Testing Navigation Endpoints ===")
    
    # Test 1: Get navigation status
    print("\n1. Getting navigation status...")
    response = requests.get(f"{BASE_URL}/api/navigation/status")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Active reservations: {data['active_reservations']}")
        print(f"   ✓ Active cooldowns: {data['active_cooldowns']}")
    else:
        print(f"   ✗ Error: {response.text}")


def main():
    """Run all API tests"""
    print("=" * 80)
    print("NPC SCHEDULING API ENDPOINT TESTS")
    print("=" * 80)
    print(f"Testing server at: {BASE_URL}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ Server is online: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Server is not running!")
        print("  Start the server with: python -m uvicorn src.server:app --port 8001 --reload")
        return 1
    
    # Run tests
    try:
        test_schedule_endpoints()
        test_dialogue_endpoints()
        test_world_memory_endpoints()
        test_navigation_endpoints()
        
        print("\n" + "=" * 80)
        print("✓ ALL API TESTS COMPLETED")
        print("=" * 80)
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
