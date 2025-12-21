"""
NPC Planning Module.
Handles daily scheduling and dynamic replanning.
"""

from __future__ import annotations
from typing import List
from src.npc.schemas import CognitiveState, DailyPlan, ScheduleEntry
import uuid

class NPCAgency:
    """
    Manages the 'Volition' of an NPC.
    """
    
    def generate_daily_schedule(self, state: CognitiveState, date_str: str, llm_client) -> DailyPlan:
        """
        Generate a new daily plan from scratch using LLM.
        """
        prompt = f"""
        You are {state.profile.name}, a {state.profile.role}.
        Traits: {', '.join(state.profile.traits)}
        Current Mood: {state.profile.current_mood}
        
        Task: Create a daily schedule for {date_str} based on your role.
        
        Strict Output Format (No other text):
        08:00 | Wake up | Quarters
        09:00 | Work | Engineering Bay
        12:00 | Lunch | Mess Hall
        13:00 | Work | Engineering Bay
        18:00 | Leisure | Recreation Deck
        22:00 | Sleep | Quarters
        
        Constraints:
        - Include valid times (HH:MM).
        - Locations must be realistic for a spaceship/station.
        """
        
        try:
            response = llm_client.generate_sync(prompt)
            entries = []
            for line in response.split('\n'):
                line = line.strip()
                if '|' in line and line[0].isdigit():
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        entries.append(ScheduleEntry(
                            time=parts[0],
                            activity=parts[1],
                            location=parts[2],
                            status="pending"
                        ))
            
            # Fallback if parsing failed
            if not entries:
                raise ValueError("No valid schedule entries parsed.")
                
            plan = DailyPlan(date=date_str, entries=entries)
            state.current_plan = plan
            return plan
            
        except Exception as e:
            print(f"[Planning Error] {e}")
            # Fallback plan
            return DailyPlan(date=date_str, entries=[
                ScheduleEntry(time="08:00", activity="Wake up", location="Quarters"),
                ScheduleEntry(time="12:00", activity="Work", location="Station"),
                ScheduleEntry(time="20:00", activity="Sleep", location="Quarters"),
            ])

    def update_plan(self, state: CognitiveState, event_description: str, llm_client) -> str:
        """
        Decide whether to alter the plan based on a new event.
        Returns the new current activity description.
        """
        if not state.current_plan:
            return "Idle"
            
        current_entry = state.current_plan.entries[state.current_plan.current_entry_index]
        
        prompt = f"""
        Current Plan: {current_entry.time} - {current_entry.activity} at {current_entry.location}
        New Event: {event_description}
        
        Task: Should {state.profile.name} abandon their current activity to deal with this event?
        Consider:
        - Urgency of event
        - Importance of current activity
        - Personality ({state.profile.traits})
        
        Output: YES or NO, followed by a short reason.
        """
        
        try:
            response = llm_client.generate_sync(prompt)
            if "YES" in response.upper():
                # Update status
                current_entry.status = "cancelled"
                return f"Reacting to: {event_description}"
            return current_entry.activity
            
        except Exception:
            return current_entry.activity
