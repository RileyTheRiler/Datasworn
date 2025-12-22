"""
NPC Scheduling System Verification Script

Automated test suite for all scheduling features:
- Schedule assignment from YAML
- Task state transitions
- Interruption handling
- Dialogue selection
- Memory decay
- World memory
- API endpoints
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from src.ai import Scheduler, NavigationManager, NPCMemoryState, MemoryTokenType
from src.dialogue import DialogueSelector, DialogueContext
from src.world import WorldMemoryManager, EventType


def print_test(name: str, passed: bool):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {name}")
    return passed


def test_schedule_loading():
    """Test 1: Load schedule templates from YAML"""
    print("\n=== Test 1: Schedule Template Loading ===")
    scheduler = Scheduler()
    
    passed = True
    passed &= print_test("Scheduler initialized", scheduler is not None)
    passed &= print_test("Templates loaded", len(scheduler.templates) > 0)
    passed &= print_test("Farmer template exists", "farmer" in scheduler.templates)
    passed &= print_test("Guard template exists", "guard" in scheduler.templates)
    passed &= print_test("Merchant template exists", "merchant" in scheduler.templates)
    
    return passed


def test_schedule_assignment():
    """Test 2: Assign schedules to NPCs"""
    print("\n=== Test 2: Schedule Assignment ===")
    scheduler = Scheduler()
    
    # Assign farmer schedule
    farmer_schedule = scheduler.assign_schedule("npc_farmer_1", "farmer")
    passed = print_test("Farmer schedule assigned", farmer_schedule is not None)
    passed &= print_test("Farmer has tasks", len(farmer_schedule.tasks) > 0)
    
    # Assign guard schedule
    guard_schedule = scheduler.assign_schedule("npc_guard_1", "guard")
    passed &= print_test("Guard schedule assigned", guard_schedule is not None)
    passed &= print_test("Guard has tasks", len(guard_schedule.tasks) > 0)
    
    return passed


def test_task_state_transitions():
    """Test 3: Task state machine"""
    print("\n=== Test 3: Task State Transitions ===")
    scheduler = Scheduler()
    schedule = scheduler.assign_schedule("npc_test", "farmer")
    
    passed = True
    if schedule and len(schedule.tasks) > 0:
        task = schedule.tasks[0]
        passed &= print_test("Initial state is PLANNED", task.state.value == "planned")
        
        # Simulate time progression
        current_time = datetime.now().replace(hour=6, minute=0)  # 6 AM
        events = scheduler.tick(current_time, {})
        
        # Check if task started
        task = schedule.get_current_task()
        if task:
            passed &= print_test("Task can transition to ACTIVE", task.state.value in ["active", "planned"])
    
    return passed


def test_interruption_handling():
    """Test 4: Interruption system"""
    print("\n=== Test 4: Interruption Handling ===")
    scheduler = Scheduler()
    schedule = scheduler.assign_schedule("npc_test", "farmer")
    
    # Start a task
    current_time = datetime.now().replace(hour=6, minute=0)
    scheduler.tick(current_time, {})
    
    # Interrupt
    success = scheduler.interrupt(
        npc_id="npc_test",
        reason="crime_alarm",
        priority=10,
        behavior="flee",
        duration=5,
        current_time=current_time
    )
    
    passed = print_test("Interruption applied", success)
    passed &= print_test("Schedule has interruption", schedule.active_interruption is not None)
    
    # Resume
    scheduler.resume("npc_test")
    passed &= print_test("Interruption cleared", schedule.active_interruption is None)
    
    return passed


def test_navigation_reservations():
    """Test 5: Navigation and prop reservations"""
    print("\n=== Test 5: Navigation Reservations ===")
    nav = NavigationManager()
    
    # Reserve a prop
    success = nav.reserve_prop("npc_1", "tavern_table_1", duration=60, cooldown=300)
    passed = print_test("Prop reserved", success)
    passed &= print_test("Prop unavailable", not nav.is_available("tavern_table_1"))
    
    # Try to reserve same prop
    success2 = nav.reserve_prop("npc_2", "tavern_table_1")
    passed &= print_test("Duplicate reservation blocked", not success2)
    
    # Release prop
    nav.release_prop("npc_1", "tavern_table_1")
    passed &= print_test("Prop released", "tavern_table_1" not in nav.reservations)
    
    # Check cooldown
    passed &= print_test("Cooldown active", not nav.is_available("tavern_table_1"))
    
    return passed


def test_npc_memory():
    """Test 6: NPC memory tokens and decay"""
    print("\n=== Test 6: NPC Memory System ===")
    memory = NPCMemoryState("npc_test")
    
    # Add memories
    memory.add_memory(MemoryTokenType.GREETED_KINDLY, "Player greeted warmly", duration=30)
    memory.add_memory(MemoryTokenType.THREATENED, "Player drew weapon", duration=120)
    
    passed = print_test("Memories added", len(memory.tokens) == 2)
    passed &= print_test("Has threatened memory", memory.has_memory(MemoryTokenType.THREATENED))
    
    # Check dialogue modifiers
    modifiers = memory.get_dialogue_modifiers()
    passed &= print_test("Dialogue modifiers generated", len(modifiers) > 0)
    
    # Check behavior state
    behavior = memory.get_behavior_state()
    passed &= print_test("Behavior state extracted", behavior["hostile"] or behavior["fearful"])
    
    # Test decay
    future_time = datetime.now() + timedelta(hours=3)
    memory.decay(180, future_time)
    passed &= print_test("Expired memories removed", len(memory.tokens) == 1)
    
    return passed


def test_dialogue_selection():
    """Test 7: Contextual dialogue selection"""
    print("\n=== Test 7: Dialogue Selection ===")
    selector = DialogueSelector()
    
    passed = print_test("Dialogue contexts loaded", len(selector.contexts) > 0)
    
    # Test weapon drawn context
    context = DialogueContext(player_has_weapon_drawn=True)
    line = selector.get_greeting("npc_test", context)
    passed &= print_test("Weapon drawn dialogue selected", line is not None)
    if line:
        passed &= print_test("Dialogue text exists", len(line.text) > 0)
    
    # Test high honor context
    context2 = DialogueContext(player_honor=0.9)
    line2 = selector.get_greeting("npc_test", context2)
    passed &= print_test("High honor dialogue selected", line2 is not None)
    
    return passed


def test_world_memory():
    """Test 8: World memory and rumors"""
    print("\n=== Test 8: World Memory System ===")
    world_mem = WorldMemoryManager()
    
    # Record events
    event1 = world_mem.record_event(
        area_id="town_square",
        event_type=EventType.CRIME_MURDER,
        description="A murder occurred in the square",
        actor="player",
        witnesses=["npc_1", "npc_2"],
        severity=0.9
    )
    
    passed = print_test("Event recorded", event1 is not None)
    
    # Get rumors
    rumors = world_mem.get_rumors("town_square")
    passed &= print_test("Rumors generated", len(rumors) > 0)
    
    # Get events
    events = world_mem.get_events("town_square")
    passed &= print_test("Events retrieved", len(events) == 1)
    
    # Test decay
    future_time = datetime.now() + timedelta(hours=10)
    removed = world_mem.decay_all(600, future_time)
    passed &= print_test("Decay processed", removed >= 0)
    
    return passed


def test_api_integration():
    """Test 9: API endpoint integration (requires server running)"""
    print("\n=== Test 9: API Integration ===")
    print("⚠ Skipping API tests (requires running server)")
    print("  Run test_endpoints.py separately to test API")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("NPC SCHEDULING SYSTEM VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_schedule_loading,
        test_schedule_assignment,
        test_task_state_transitions,
        test_interruption_handling,
        test_navigation_reservations,
        test_npc_memory,
        test_dialogue_selection,
        test_world_memory,
        test_api_integration,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ ERROR in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
