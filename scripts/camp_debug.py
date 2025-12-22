"""
Camp System Debug Tool.

Interactive CLI for inspecting and testing the living hub/camp system.
Features:
- View current routines and activities
- Check/Trigger events
- Inspect NPC status
- Visualize dialogue threads
"""

import sys
import time
import argparse
from typing import Dict, Any, List
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.narrative.camp_layout import get_camp_layout_dict, get_zone
from src.narrative.camp_routines import (
    get_routine, get_all_routines, get_current_activities,
    get_npcs_at_location, Weather, Season
)
from src.narrative.camp_dialogue import get_camp_dialogue, CampDialogueContext
from src.narrative.hub_interactions import HubInteractionManager
from src.narrative.camp_arcs import CampArcManager
from src.narrative.camp_events import CampEventManager
from src.narrative.camp_journal import CampJournal


class CampDebugger:
    def __init__(self):
        self.interaction_mgr = HubInteractionManager()
        self.arc_mgr = CampArcManager()
        self.event_mgr = CampEventManager()
        self.journal = CampJournal()
        self.current_hour = 12
        self.weather = Weather.CLEAR
        self.season = Season.SUMMER
    
    def print_status(self):
        print("\n" + "=" * 60)
        print(f"CAMP STATUS - Hour: {self.current_hour:02d}:00 | Weather: {self.weather.value} | Season: {self.season.value}")
        print("-" * 60)
        print(f"Crew Morale: {self.arc_mgr.crew_morale:.2f}")
        print(f"Active Event: {self.event_mgr.active_event.name if self.event_mgr.active_event else 'None'}")
        print("=" * 60)
    
    def show_activities(self):
        print("\nCURRENT ACTIVITIES:")
        activities = get_current_activities(self.current_hour, self.weather, self.season)
        
        # Group by location
        by_loc = {}
        for npc, act in activities.items():
            if act.location not in by_loc:
                by_loc[act.location] = []
            by_loc[act.location].append((npc, act))
        
        for loc, npcs in  by_loc.items():
            zone = get_zone(loc)
            print(f"📍 {zone.name} ({loc})")
            for npc, act in npcs:
                status = "INT" if act.interruptible else "BUSY"
                print(f"  • {npc.upper():<8} [{status}] {act.activity} ({act.intent.value})")
    
    def show_arcs(self):
        print("\nNPC STATUS:")
        print(f"{'NAME':<10} {'REL':<5} {'MOR':<5} {'STEP':<15} {'FLAGS'}")
        print("-" * 60)
        
        for npc in ["yuki", "torres", "kai", "okonkwo", "vasquez", "ember"]:
            state = self.arc_mgr.get_arc_state(npc)
            flags = ", ".join(state.flags) if state.flags else "-"
            print(f"{npc.upper():<10} {state.relationship_level:.2f}  {state.morale:.2f}  {state.current_step.value:<15} {flags}")
    
    def trigger_event(self):
        print("\nAVAILABLE EVENTS:")
        events = self.event_mgr.camp_events
        for i, (eid, evt) in enumerate(events.items()):
            print(f"{i+1}. {evt.name} ({evt.event_type.value})")
        
        try:
            choice = int(input("Select event to trigger (0 to cancel): "))
            if 0 < choice <= len(events):
                eid = list(events.keys())[choice-1]
                dialogue = self.event_mgr.start_event(eid)
                if dialogue:
                    print(f"\n[EVENT STARTED] {self.event_mgr.active_event.name}")
                    print(f"{dialogue.speaker.upper()}: {dialogue.text}")
                    self._play_event()
                else:
                    print("Failed to start event.")
        except ValueError:
            pass
    
    def _play_event(self):
        while True:
            cmd = input("\n[Adv]ance, [Q]uit event: ").lower()
            if cmd == 'q':
                break
            
            dialogue = self.event_mgr.advance_event()
            if not dialogue:
                print("[EVENT ENDED]")
                break
            
            print(f"{dialogue.speaker.upper()}: {dialogue.text}")
            if dialogue.reactions:
                for reactor, react in dialogue.reactions.items():
                    print(f"  > {reactor}: {react}")
    
    def simulate_interaction(self):
        npc = input("Enter NPC ID to interact with (e.g. torres): ").lower()
        if not get_routine(npc):
            print("NPC not found.")
            return
            
        print(f"\nInitiating interaction with {npc}...")
        seq = self.interaction_mgr.initiate_walk_and_talk(npc)
        print(f"CONTEXT: {seq.context}")
        
        dlg = seq.get_current_dialogue()
        print(f"{npc.upper()}: {dlg}")
        
        while seq.is_active:
            cmd = input("\n[N]ext leg, [A]bort, [Q]uit: ").lower()
            if cmd == 'q':
                break
            elif cmd == 'a':
                bye = self.interaction_mgr.abort_interaction(npc)
                print(f"{npc.upper()}: {bye}")
                break
            else:
                dlg = self.interaction_mgr.advance_sequence(npc)
                if dlg:
                     print(f"{npc.upper()}: {dlg}")
                else:
                    print("[INTERACTION ENDED]")
                    break

    def run(self):
        while True:
            self.print_status()
            print("\nCOMMANDS:")
            print("1. Show Activities")
            print("2. Show NPC Status (Arcs)")
            print("3. Check/Trigger Events")
            print("4. Simulate Interaction")
            print("5. Advance Time (+1h)")
            print("6. Change Weather")
            print("Q. Quit")
            
            choice = input("\nSelect option: ").lower()
            
            if choice == 'q':
                break
            elif choice == '1':
                self.show_activities()
            elif choice == '2':
                self.show_arcs()
            elif choice == '3':
                self.trigger_event()
            elif choice == '4':
                self.simulate_interaction()
            elif choice == '5':
                self.current_hour = (self.current_hour + 1) % 24
            elif choice == '6':
                w = input("Weather (clear/rain/storm/snow): ").upper()
                try:
                    self.weather = Weather[w]
                except:
                    print("Invalid weather")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    debugger = CampDebugger()
    debugger.run()
