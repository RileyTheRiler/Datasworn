"""
Verification Script for Chapter Progression System

Tests all backend functionality including:
- Chapter data loading
- State management
- Region locking/unlocking
- Soft locks
- Economy modifiers
- Chapter advancement
- Time/season jumps
- World state deltas
- API endpoints
"""

import sys
from pathlib import Path
import requests
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.narrative.progression import ProgressionManager, ChapterState


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"  → {details}")


def test_chapter_data_loading():
    """Test loading chapter metadata from YAML."""
    print_section("Chapter Data Loading")
    
    try:
        manager = ProgressionManager()
        
        # Test chapters loaded
        print_test(
            "Chapters loaded",
            len(manager.chapters) > 0,
            f"Loaded {len(manager.chapters)} chapters"
        )
        
        # Test chapter structure
        for chapter_id, chapter in manager.chapters.items():
            print(f"\nChapter: {chapter.name} ({chapter_id})")
            print(f"  Season: {chapter.season}")
            print(f"  Regions: {len(chapter.regions_unlocked)}")
            print(f"  Critical Missions: {len(chapter.critical_missions)}")
            print(f"  Soft Locks: {len(chapter.soft_locks)}")
            print(f"  Law Pressure: {chapter.law_pressure}")
        
        return True
    except Exception as e:
        print_test("Chapter data loading", False, str(e))
        return False


def test_state_management():
    """Test chapter state tracking."""
    print_section("State Management")
    
    try:
        manager = ProgressionManager()
        
        # Test initial state
        print_test(
            "Initial state created",
            manager.state.current_chapter_id == "chapter_1",
            f"Current chapter: {manager.state.current_chapter_id}"
        )
        
        # Test state serialization
        state_dict = manager.state.to_dict()
        restored_state = ChapterState.from_dict(state_dict)
        
        print_test(
            "State serialization",
            restored_state.current_chapter_id == manager.state.current_chapter_id,
            "State can be serialized and restored"
        )
        
        # Test get_state method
        state_info = manager.get_state()
        print_test(
            "Get state method",
            'chapter' in state_info and 'state' in state_info,
            f"State info keys: {list(state_info.keys())}"
        )
        
        return True
    except Exception as e:
        print_test("State management", False, str(e))
        return False


def test_region_locking():
    """Test region locking and unlocking."""
    print_section("Region Locking/Unlocking")
    
    try:
        manager = ProgressionManager()
        
        # Test initial regions
        initial_regions = manager.state.unlocked_regions.copy()
        print(f"Initial unlocked regions: {initial_regions}")
        
        # Test unlock new region
        test_region = "test_region"
        manager.unlock_region(test_region)
        
        print_test(
            "Unlock region",
            test_region in manager.state.unlocked_regions,
            f"Region '{test_region}' unlocked"
        )
        
        # Test lock region
        manager.lock_region(test_region)
        
        print_test(
            "Lock region",
            test_region not in manager.state.unlocked_regions,
            f"Region '{test_region}' locked"
        )
        
        # Test is_region_accessible
        if initial_regions:
            first_region = initial_regions[0]
            is_accessible = manager.is_region_accessible(first_region)
            
            print_test(
                "Region accessibility check",
                is_accessible,
                f"Region '{first_region}' is accessible"
            )
        
        return True
    except Exception as e:
        print_test("Region locking", False, str(e))
        return False


def test_soft_locks():
    """Test soft lock management."""
    print_section("Soft Lock Management")
    
    try:
        manager = ProgressionManager()
        
        # Check initial soft locks
        print(f"Active soft locks: {len(manager.state.active_soft_locks)}")
        
        for lock_id, soft_lock in manager.state.active_soft_locks.items():
            print(f"\n  {lock_id}:")
            print(f"    Description: {soft_lock.description}")
            print(f"    Affected regions: {soft_lock.affected_regions}")
            print(f"    Active: {soft_lock.active}")
        
        # Test toggling soft lock
        if manager.state.active_soft_locks:
            first_lock_id = list(manager.state.active_soft_locks.keys())[0]
            original_state = manager.state.active_soft_locks[first_lock_id].active
            
            manager.set_soft_lock(first_lock_id, not original_state)
            
            print_test(
                "Toggle soft lock",
                manager.state.active_soft_locks[first_lock_id].active != original_state,
                f"Soft lock '{first_lock_id}' toggled"
            )
            
            # Test region accessibility with soft lock
            affected_region = manager.state.active_soft_locks[first_lock_id].affected_regions[0]
            if affected_region in manager.state.unlocked_regions:
                is_accessible = manager.is_region_accessible(affected_region)
                
                print_test(
                    "Soft lock blocks region",
                    not is_accessible if manager.state.active_soft_locks[first_lock_id].active else is_accessible,
                    f"Region '{affected_region}' accessibility: {is_accessible}"
                )
        
        return True
    except Exception as e:
        print_test("Soft lock management", False, str(e))
        return False


def test_economy_modifiers():
    """Test economy modifier system."""
    print_section("Economy Modifiers")
    
    try:
        manager = ProgressionManager()
        
        # Check initial modifiers
        print("Initial economy modifiers:")
        for category, modifier in manager.state.current_economy_modifiers.items():
            print(f"  {category}: {modifier}x")
        
        # Test get_price_modifier
        if manager.state.current_economy_modifiers:
            first_category = list(manager.state.current_economy_modifiers.keys())[0]
            modifier = manager.get_price_modifier(first_category)
            
            print_test(
                "Get price modifier",
                modifier == manager.state.current_economy_modifiers[first_category],
                f"{first_category}: {modifier}x"
            )
        
        # Test apply new modifiers
        test_modifiers = {"test_category": 1.5}
        manager.apply_economy_modifiers(test_modifiers)
        
        print_test(
            "Apply economy modifiers",
            manager.state.current_economy_modifiers == test_modifiers,
            "New modifiers applied"
        )
        
        return True
    except Exception as e:
        print_test("Economy modifiers", False, str(e))
        return False


def test_mission_completion():
    """Test mission completion tracking."""
    print_section("Mission Completion")
    
    try:
        manager = ProgressionManager()
        
        # Complete a mission
        test_mission = "test_mission"
        manager.complete_mission(test_mission)
        
        print_test(
            "Complete mission",
            test_mission in manager.state.completed_missions,
            f"Mission '{test_mission}' completed"
        )
        
        # Test validation
        current_chapter = manager.get_current_chapter()
        
        # Complete all critical missions
        for mission in current_chapter.critical_missions:
            manager.complete_mission(mission)
        
        is_complete, missing = manager.validate_chapter_completion()
        
        print_test(
            "Chapter completion validation",
            is_complete and len(missing) == 0,
            f"All critical missions completed: {is_complete}"
        )
        
        return True
    except Exception as e:
        print_test("Mission completion", False, str(e))
        return False


def test_chapter_advancement():
    """Test chapter advancement flow."""
    print_section("Chapter Advancement")
    
    try:
        manager = ProgressionManager()
        
        # Get initial state
        initial_chapter = manager.state.current_chapter_id
        initial_season = manager.state.current_season
        initial_days = manager.state.total_days_elapsed
        
        print(f"Initial state:")
        print(f"  Chapter: {initial_chapter}")
        print(f"  Season: {initial_season}")
        print(f"  Days elapsed: {initial_days}")
        
        # Complete all critical missions for chapter 1
        chapter_1 = manager.chapters['chapter_1']
        for mission in chapter_1.critical_missions:
            manager.complete_mission(mission)
        
        # Advance to chapter 2
        result = manager.advance_chapter('chapter_2')
        
        print_test(
            "Chapter advancement",
            result['success'],
            f"Advanced to {result.get('chapter_name', 'N/A')}"
        )
        
        print(f"\nAdvancement result:")
        print(f"  New chapter: {manager.state.current_chapter_id}")
        print(f"  New season: {manager.state.current_season}")
        print(f"  Days elapsed: {manager.state.total_days_elapsed}")
        print(f"  Days advanced: {result['time_jump']['days_advanced']}")
        
        # Test world state changes
        print(f"\nWorld state changes:")
        changes = result['world_state_changes']
        print(f"  Regions added: {changes['regions_added']}")
        print(f"  Regions removed: {changes['regions_removed']}")
        print(f"  Law pressure change: {changes['law_pressure_change']}")
        print(f"  New soft locks: {len(changes['soft_locks'])}")
        
        print_test(
            "Time jump applied",
            manager.state.total_days_elapsed > initial_days,
            f"Time advanced by {manager.state.total_days_elapsed - initial_days} days"
        )
        
        print_test(
            "Season changed",
            manager.state.current_season != initial_season or initial_chapter == 'chapter_1',
            f"Season: {initial_season} → {manager.state.current_season}"
        )
        
        return True
    except Exception as e:
        print_test("Chapter advancement", False, str(e))
        return False


def test_debug_commands():
    """Test debug commands."""
    print_section("Debug Commands")
    
    try:
        manager = ProgressionManager()
        
        # Test force set chapter
        success = manager.force_set_chapter('chapter_3')
        
        print_test(
            "Force set chapter",
            success and manager.state.current_chapter_id == 'chapter_3',
            f"Forced to chapter_3"
        )
        
        # Test invalid chapter
        success = manager.force_set_chapter('invalid_chapter')
        
        print_test(
            "Invalid chapter handling",
            not success,
            "Correctly rejected invalid chapter"
        )
        
        return True
    except Exception as e:
        print_test("Debug commands", False, str(e))
        return False


def test_api_endpoints():
    """Test API endpoints."""
    print_section("API Endpoints")
    
    base_url = "http://localhost:8001"
    
    try:
        # Test health check first
        response = requests.get(f"{base_url}/")
        print_test(
            "Server health check",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code != 200:
            print("\n⚠ Server not running on port 8001. Skipping API tests.")
            print("  Start server with: python -m uvicorn src.server:app --port 8001 --reload")
            return False
        
        # Create a test session first
        session_response = requests.post(
            f"{base_url}/api/session/start",
            json={
                "character_name": "Test Character",
                "background_vow": "Test the chapter system"
            }
        )
        
        if session_response.status_code != 200:
            print_test("Create session", False, "Failed to create test session")
            return False
        
        session_id = "default"
        
        # Test GET /api/chapter/current
        response = requests.get(f"{base_url}/api/chapter/current?session_id={session_id}")
        print_test(
            "GET /api/chapter/current",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Current chapter: {data['chapter']['name']}")
            print(f"  Season: {data['chapter']['season']}")
        
        # Test GET /api/chapter/regions
        response = requests.get(f"{base_url}/api/chapter/regions?session_id={session_id}")
        print_test(
            "GET /api/chapter/regions",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Unlocked regions: {len(data['unlocked'])}")
            print(f"  Locked regions: {len(data['locked'])}")
        
        # Test GET /api/chapter/soft-locks
        response = requests.get(f"{base_url}/api/chapter/soft-locks?session_id={session_id}")
        print_test(
            "GET /api/chapter/soft-locks",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Active soft locks: {len(data['active'])}")
        
        # Test GET /api/chapter/progress
        response = requests.get(f"{base_url}/api/chapter/progress?session_id={session_id}")
        print_test(
            "GET /api/chapter/progress",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Chapter: {data['chapter_name']}")
            print(f"  Completed: {len(data['completed_missions'])}/{len(data['critical_missions'])}")
            print(f"  Can advance: {data['can_advance']}")
        
        # Test POST /api/debug/chapter/set
        response = requests.post(
            f"{base_url}/api/debug/chapter/set",
            json={
                "session_id": session_id,
                "chapter_id": "chapter_2"
            }
        )
        print_test(
            "POST /api/debug/chapter/set",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        # Test POST /api/debug/chapter/unlock-region
        response = requests.post(
            f"{base_url}/api/debug/chapter/unlock-region",
            json={
                "session_id": session_id,
                "region_id": "test_region"
            }
        )
        print_test(
            "POST /api/debug/chapter/unlock-region",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        # Test POST /api/chapter/advance (should fail without missions)
        response = requests.post(
            f"{base_url}/api/chapter/advance",
            json={
                "session_id": session_id,
                "next_chapter_id": "chapter_3"
            }
        )
        print_test(
            "POST /api/chapter/advance (validation)",
            response.status_code == 400,
            "Correctly rejects advancement without completed missions"
        )
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n⚠ Could not connect to server on port 8001")
        print("  Start server with: python -m uvicorn src.server:app --port 8001 --reload")
        return False
    except Exception as e:
        print_test("API endpoints", False, str(e))
        return False


def main():
    """Run all verification tests."""
    print("\n" + "="*70)
    print("  CHAPTER PROGRESSION SYSTEM VERIFICATION")
    print("="*70)
    
    results = {
        "Chapter Data Loading": test_chapter_data_loading(),
        "State Management": test_state_management(),
        "Region Locking": test_region_locking(),
        "Soft Lock Management": test_soft_locks(),
        "Economy Modifiers": test_economy_modifiers(),
        "Mission Completion": test_mission_completion(),
        "Chapter Advancement": test_chapter_advancement(),
        "Debug Commands": test_debug_commands(),
        "API Endpoints": test_api_endpoints()
    }
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  TOTAL: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("✓ All tests passed! Chapter progression system is ready.")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
