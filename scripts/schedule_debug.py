"""
Interactive NPC Schedule Debugger

Visualize active schedules, memory tokens, and dialogue picks in real-time.
Includes time-skip controls and filtering by region/archetype.
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
import json


class ScheduleDebugger:
    """Interactive debugger for NPC schedules"""
    
    def __init__(self):
        self.scheduler = Scheduler()
        self.navigation = NavigationManager()
        self.dialogue_selector = DialogueSelector()
        self.world_memory = WorldMemoryManager()
        self.npc_memories = {}
        self.current_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        
        # Create some test NPCs
        self.setup_test_npcs()
    
    def setup_test_npcs(self):
        """Create test NPCs with schedules"""
        print("Setting up test NPCs...")
        
        # Assign schedules
        self.scheduler.assign_schedule("farmer_john", "farmer", "default", self.current_time)
        self.scheduler.assign_schedule("guard_sarah", "guard", "default", self.current_time)
        self.scheduler.assign_schedule("merchant_bob", "merchant", "default", self.current_time)
        
        # Create memory states
        self.npc_memories["farmer_john"] = NPCMemoryState("farmer_john")
        self.npc_memories["guard_sarah"] = NPCMemoryState("guard_sarah")
        self.npc_memories["merchant_bob"] = NPCMemoryState("merchant_bob")
        
        print(f"✓ Created 3 NPCs with schedules")
    
    def display_schedules(self, filter_archetype=None):
        """Display all active schedules"""
        print("\n" + "=" * 80)
        print(f"ACTIVE SCHEDULES - {self.current_time.strftime('%H:%M')}")
        print("=" * 80)
        
        schedules = self.scheduler.get_all_active_schedules()
        
        for npc_id, schedule in schedules.items():
            if filter_archetype and schedule.archetype != filter_archetype:
                continue
            
            current_task = schedule.get_current_task()
            next_task = schedule.get_next_task()
            
            print(f"\n📋 {npc_id.upper()} ({schedule.archetype})")
            print(f"   Progress: {schedule.current_task_index}/{len(schedule.tasks)} tasks")
            
            if schedule.active_interruption:
                print(f"   ⚠ INTERRUPTED: {schedule.active_interruption.reason}")
                print(f"      Behavior: {schedule.active_interruption.behavior}")
            elif current_task:
                print(f"   Current: [{current_task.state.value.upper()}] {current_task.behavior}")
                print(f"            @ {current_task.location} ({current_task.time})")
                print(f"            {current_task.description}")
            
            if next_task:
                print(f"   Next:    {next_task.behavior} @ {next_task.location} ({next_task.time})")
    
    def display_memory_tokens(self, npc_id=None):
        """Display memory tokens for NPCs"""
        print("\n" + "=" * 80)
        print("NPC MEMORY TOKENS")
        print("=" * 80)
        
        npcs_to_show = [npc_id] if npc_id else self.npc_memories.keys()
        
        for npc in npcs_to_show:
            if npc not in self.npc_memories:
                continue
            
            memory = self.npc_memories[npc]
            print(f"\n🧠 {npc.upper()}")
            
            if not memory.tokens:
                print("   No memories")
                continue
            
            for token in memory.tokens:
                age = token.get_age(self.current_time)
                decay = token.get_decay_factor(self.current_time)
                print(f"   • {token.token_type.value}")
                print(f"     Context: {token.context}")
                print(f"     Age: {age:.1f}m | Decay: {decay:.2f} | Intensity: {token.intensity:.2f}")
            
            # Show behavior state
            behavior = memory.get_behavior_state(self.current_time)
            active_states = [k for k, v in behavior.items() if v]
            if active_states:
                print(f"   Behavior: {', '.join(active_states)}")
    
    def display_dialogue_test(self, npc_id, context_dict=None):
        """Test dialogue selection for an NPC"""
        print("\n" + "=" * 80)
        print(f"DIALOGUE TEST - {npc_id.upper()}")
        print("=" * 80)
        
        # Build context
        context = DialogueContext(**(context_dict or {}))
        
        print(f"\nContext:")
        print(f"  Player weapon drawn: {context.player_has_weapon_drawn}")
        print(f"  Player honor: {context.player_honor:.2f}")
        print(f"  Weather: {context.weather}")
        print(f"  Time: {context.time_of_day}")
        
        # Get greeting
        greeting = self.dialogue_selector.get_greeting(npc_id, context)
        if greeting:
            print(f"\nGreeting:")
            print(f"  \"{greeting.text}\"")
            if greeting.animation:
                print(f"  Animation: {greeting.animation}")
        
        # Get walk-by bark
        bark = self.dialogue_selector.get_walk_by_bark(npc_id, context)
        if bark:
            print(f"\nWalk-by Bark:")
            print(f"  \"{bark.text}\"")
    
    def display_world_memory(self, area_id="town_square"):
        """Display world memory for an area"""
        print("\n" + "=" * 80)
        print(f"WORLD MEMORY - {area_id.upper()}")
        print("=" * 80)
        
        rumors = self.world_memory.get_rumors(area_id, self.current_time, limit=5)
        events = self.world_memory.get_events(area_id, current_time=self.current_time)
        
        print(f"\nRumors ({len(rumors)}):")
        for rumor in rumors:
            print(f"  • {rumor}")
        
        print(f"\nRecent Events ({len(events)}):")
        for event in events:
            age = event.get_age(self.current_time)
            print(f"  • [{event.event_type.value}] {event.description}")
            print(f"    Age: {age:.1f}m | Severity: {event.severity:.2f}")
    
    def time_skip(self, hours=0, minutes=0):
        """Skip forward in time"""
        delta = timedelta(hours=hours, minutes=minutes)
        self.current_time += delta
        
        # Tick scheduler
        events = self.scheduler.tick(self.current_time, {})
        
        # Decay memories
        for memory in self.npc_memories.values():
            memory.decay(int(delta.total_seconds() / 60), self.current_time)
        
        # Decay world memory
        self.world_memory.decay_all(int(delta.total_seconds() / 60), self.current_time)
        
        print(f"\n⏰ Time advanced to {self.current_time.strftime('%H:%M')}")
        if events["task_started"]:
            print(f"   Tasks started: {len(events['task_started'])}")
        if events["task_completed"]:
            print(f"   Tasks completed: {len(events['task_completed'])}")
    
    def add_test_memory(self, npc_id, token_type, context):
        """Add a test memory to an NPC"""
        if npc_id in self.npc_memories:
            self.npc_memories[npc_id].add_memory(
                token_type=token_type,
                context=context,
                current_time=self.current_time
            )
            print(f"✓ Added {token_type.value} memory to {npc_id}")
    
    def add_test_event(self, area_id, event_type, description):
        """Add a test event to world memory"""
        self.world_memory.record_event(
            area_id=area_id,
            event_type=event_type,
            description=description,
            current_time=self.current_time
        )
        print(f"✓ Recorded {event_type.value} in {area_id}")
    
    def export_state(self, filename="debug_state.json"):
        """Export current state to JSON"""
        state = {
            "current_time": self.current_time.isoformat(),
            "schedules": {
                npc_id: sched.to_dict()
                for npc_id, sched in self.scheduler.get_all_active_schedules().items()
            },
            "memories": {
                npc_id: mem.to_dict()
                for npc_id, mem in self.npc_memories.items()
            },
            "world_memory": self.world_memory.get_status(),
            "navigation": self.navigation.get_status(),
        }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"✓ State exported to {filename}")
    
    def interactive_menu(self):
        """Interactive menu"""
        while True:
            print("\n" + "=" * 80)
            print("SCHEDULE DEBUGGER - MENU")
            print("=" * 80)
            print("1. View all schedules")
            print("2. View memory tokens")
            print("3. Test dialogue")
            print("4. View world memory")
            print("5. Time skip (1 hour)")
            print("6. Time skip (custom)")
            print("7. Add test memory")
            print("8. Add test event")
            print("9. Trigger interruption")
            print("10. Export state")
            print("0. Exit")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                archetype = input("Filter by archetype (or Enter for all): ").strip() or None
                self.display_schedules(archetype)
            
            elif choice == "2":
                npc_id = input("NPC ID (or Enter for all): ").strip() or None
                self.display_memory_tokens(npc_id)
            
            elif choice == "3":
                npc_id = input("NPC ID: ").strip()
                weapon = input("Player has weapon drawn? (y/n): ").lower() == 'y'
                honor = float(input("Player honor (0.0-1.0): ") or "0.5")
                context = {"player_has_weapon_drawn": weapon, "player_honor": honor}
                self.display_dialogue_test(npc_id, context)
            
            elif choice == "4":
                area = input("Area ID (default: town_square): ").strip() or "town_square"
                self.display_world_memory(area)
            
            elif choice == "5":
                self.time_skip(hours=1)
            
            elif choice == "6":
                hours = int(input("Hours: ") or "0")
                minutes = int(input("Minutes: ") or "0")
                self.time_skip(hours=hours, minutes=minutes)
            
            elif choice == "7":
                npc_id = input("NPC ID: ").strip()
                print("Token types: GREETED_KINDLY, THREATENED, WITNESSED_CRIME, etc.")
                token_str = input("Token type: ").strip().upper()
                context = input("Context: ").strip()
                try:
                    token_type = MemoryTokenType[token_str]
                    self.add_test_memory(npc_id, token_type, context)
                except KeyError:
                    print("Invalid token type")
            
            elif choice == "8":
                area = input("Area ID: ").strip()
                print("Event types: CRIME_MURDER, CRIME_THEFT, HEROIC_RESCUE, etc.")
                event_str = input("Event type: ").strip().upper()
                desc = input("Description: ").strip()
                try:
                    event_type = EventType[event_str]
                    self.add_test_event(area, event_type, desc)
                except KeyError:
                    print("Invalid event type")
            
            elif choice == "9":
                npc_id = input("NPC ID: ").strip()
                reason = input("Reason: ").strip()
                priority = int(input("Priority (1-10): ") or "8")
                behavior = input("Behavior: ").strip()
                self.scheduler.interrupt(npc_id, reason, priority, behavior, current_time=self.current_time)
                print(f"✓ Interrupted {npc_id}")
            
            elif choice == "10":
                filename = input("Filename (default: debug_state.json): ").strip() or "debug_state.json"
                self.export_state(filename)
            
            elif choice == "0":
                print("Goodbye!")
                break


def main():
    """Main entry point"""
    print("=" * 80)
    print("NPC SCHEDULE DEBUGGER")
    print("=" * 80)
    
    debugger = ScheduleDebugger()
    
    # Show initial state
    debugger.display_schedules()
    
    # Start interactive menu
    debugger.interactive_menu()


if __name__ == "__main__":
    main()
