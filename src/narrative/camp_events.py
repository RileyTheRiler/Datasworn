"""
Camp Events System.

Manages shared camp events like meals, celebrations, arguments,
and crisis meetings triggered by world state.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import random


class EventType(Enum):
    """Types of camp events."""
    MEAL = "meal"
    CELEBRATION = "celebration"
    ARGUMENT = "argument"
    CRISIS_MEETING = "crisis_meeting"
    MEMORIAL = "memorial"
    TRAINING = "training"
    STORYTELLING = "storytelling"
    GAME_NIGHT = "game_night"


@dataclass
class EventTrigger:
    """Conditions that trigger an event."""
    morale_min: Optional[float] = None
    morale_max: Optional[float] = None
    recent_success: bool = False
    recent_failure: bool = False
    time_of_day_required: Optional[str] = None  # "morning", "evening", etc.
    npcs_required: Optional[list[str]] = None
    cooldown_hours: int = 24


@dataclass
class EventDialoguePart:
    """A single part of an event's multi-part dialogue."""
    speaker: str
    text: str
    reactions: dict[str, str] = field(default_factory=dict)  # npc_id -> reaction


@dataclass
class CampEvent:
    """A shared camp event."""
    event_id: str
    event_type: EventType
    name: str
    description: str
    trigger: EventTrigger
    participants: list[str]  # NPC IDs
    dialogue_parts: list[EventDialoguePart] = field(default_factory=list)
    morale_effect: float = 0.0
    last_triggered: int = -999  # Hour last triggered
    
    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "name": self.name,
            "description": self.description,
            "participants": self.participants,
            "morale_effect": self.morale_effect,
        }


# =============================================================================
# PREDEFINED CAMP EVENTS
# =============================================================================

CAMP_EVENTS = {
    "evening_meal": CampEvent(
        event_id="evening_meal",
        event_type=EventType.MEAL,
        name="Evening Meal",
        description="The crew gathers for dinner around the fire.",
        trigger=EventTrigger(
            time_of_day_required="evening",
            cooldown_hours=24
        ),
        participants=["torres", "kai", "okonkwo", "vasquez", "ember"],
        dialogue_parts=[
            EventDialoguePart(
                speaker="torres",
                text="*serves food* Alright everyone, dig in. Made extra tonight.",
                reactions={
                    "vasquez": "*grins* Finally, something good!",
                    "ember": "*eyes light up* This smells amazing!",
                }
            ),
            EventDialoguePart(
                speaker="okonkwo",
                text="*raises cup* To another day survived.",
                reactions={
                    "kai": "*quiet* To survival.",
                    "torres": "*nods* And to better days ahead.",
                }
            ),
        ],
        morale_effect=0.05
    ),
    
    "victory_celebration": CampEvent(
        event_id="victory_celebration",
        event_type=EventType.CELEBRATION,
        name="Victory Celebration",
        description="The crew celebrates a successful mission.",
        trigger=EventTrigger(
            recent_success=True,
            morale_min=0.4,
            cooldown_hours=48
        ),
        participants=["yuki", "torres", "kai", "okonkwo", "vasquez", "ember"],
        dialogue_parts=[
            EventDialoguePart(
                speaker="vasquez",
                text="*raises bottle* We did it! We actually pulled it off!",
                reactions={
                    "torres": "*laughs* Never doubted us for a second!",
                    "ember": "*bouncing* That was incredible!",
                }
            ),
            EventDialoguePart(
                speaker="yuki",
                text="*rare smile* Good work, everyone. Really.",
                reactions={
                    "kai": "*surprised* Did Yuki just... smile?",
                    "okonkwo": "*warm* We make a good team.",
                }
            ),
        ],
        morale_effect=0.15
    ),
    
    "tension_argument": CampEvent(
        event_id="tension_argument",
        event_type=EventType.ARGUMENT,
        name="Heated Argument",
        description="Stress boils over into conflict.",
        trigger=EventTrigger(
            morale_max=0.3,
            recent_failure=True,
            cooldown_hours=72
        ),
        participants=["yuki", "torres", "vasquez"],
        dialogue_parts=[
            EventDialoguePart(
                speaker="vasquez",
                text="*angry* This is exactly what I was talking about! We're not prepared!",
                reactions={
                    "torres": "*defensive* We did the best we could!",
                    "yuki": "*cold* Enough. Both of you.",
                }
            ),
            EventDialoguePart(
                speaker="torres",
                text="*frustrated* Maybe if someone had checked the supplies properly—",
                reactions={
                    "vasquez": "*stands* Are you blaming ME?",
                    "okonkwo": "*intervenes* Everyone, please. This isn't helping.",
                }
            ),
        ],
        morale_effect=-0.10
    ),
    
    "crisis_meeting": CampEvent(
        event_id="crisis_meeting",
        event_type=EventType.CRISIS_MEETING,
        name="Emergency Meeting",
        description="The crew gathers to discuss a serious situation.",
        trigger=EventTrigger(
            morale_max=0.4,
            npcs_required=["yuki", "torres", "okonkwo"],
            cooldown_hours=48
        ),
        participants=["yuki", "torres", "kai", "okonkwo", "vasquez", "ember"],
        dialogue_parts=[
            EventDialoguePart(
                speaker="yuki",
                text="*serious* We need to talk. All of us. Now.",
                reactions={
                    "kai": "*worried* What's wrong?",
                    "ember": "*nervous* Are we in danger?",
                }
            ),
            EventDialoguePart(
                speaker="okonkwo",
                text="*calm* Let's hear everyone out. We're stronger together.",
                reactions={
                    "torres": "*nods* The doctor's right. We figure this out as a team.",
                }
            ),
        ],
        morale_effect=0.05  # Addressing problems helps
    ),
    
    "storytelling_night": CampEvent(
        event_id="storytelling_night",
        event_type=EventType.STORYTELLING,
        name="Stories by the Fire",
        description="The crew shares stories and memories.",
        trigger=EventTrigger(
            time_of_day_required="night",
            morale_min=0.5,
            cooldown_hours=72
        ),
        participants=["torres", "kai", "okonkwo", "vasquez", "ember"],
        dialogue_parts=[
            EventDialoguePart(
                speaker="torres",
                text="*by the fire* Anyone want to hear about the time I outran a patrol ship in an asteroid field?",
                reactions={
                    "ember": "*excited* Yes! Tell us!",
                    "vasquez": "*grins* This should be good.",
                }
            ),
            EventDialoguePart(
                speaker="kai",
                text="*quiet* I have a story too. About... before.",
                reactions={
                    "okonkwo": "*encouraging* We're listening.",
                    "torres": "*gentle* Take your time.",
                }
            ),
        ],
        morale_effect=0.08
    ),
    
    "memorial_moment": CampEvent(
        event_id="memorial_moment",
        event_type=EventType.MEMORIAL,
        name="Remembering the Fallen",
        description="A quiet moment to remember those lost.",
        trigger=EventTrigger(
            morale_max=0.5,
            time_of_day_required="evening",
            cooldown_hours=168  # Once a week max
        ),
        participants=["yuki", "torres", "kai", "okonkwo", "vasquez", "ember"],
        dialogue_parts=[
            EventDialoguePart(
                speaker="okonkwo",
                text="*lights candle* For those who aren't with us anymore.",
                reactions={
                    "yuki": "*quiet* ...Captain Reyes.",
                    "torres": "*somber* And all the others.",
                }
            ),
            EventDialoguePart(
                speaker="ember",
                text="*soft* Do you think they'd be proud of us?",
                reactions={
                    "kai": "*gentle* I think they would.",
                    "vasquez": "*nods* We're still fighting. That counts for something.",
                }
            ),
        ],
        morale_effect=0.03  # Bittersweet but important
    ),
}


# =============================================================================
# EVENT MANAGER
# =============================================================================

class CampEventManager:
    """Manages camp event triggering and execution."""
    
    def __init__(self):
        self.events = CAMP_EVENTS.copy()
        self.active_event: Optional[CampEvent] = None
        self.current_event_part: int = 0
        self.current_hour: int = 12
        self.recent_mission_success: bool = False
        self.recent_mission_failure: bool = False
    
    def check_triggers(
        self,
        crew_morale: float,
        hour: int,
        available_npcs: list[str]
    ) -> Optional[CampEvent]:
        """
        Check if any events should trigger.
        Returns the highest priority triggered event.
        """
        self.current_hour = hour
        
        from src.daily_scripts import get_time_of_day
        time_of_day = get_time_of_day(hour).value
        
        triggered_events = []
        
        for event in self.events.values():
            trigger = event.trigger
            
            # Check cooldown
            if hour - event.last_triggered < trigger.cooldown_hours:
                continue
            
            # Check morale range
            if trigger.morale_min is not None and crew_morale < trigger.morale_min:
                continue
            if trigger.morale_max is not None and crew_morale > trigger.morale_max:
                continue
            
            # Check mission results
            if trigger.recent_success and not self.recent_mission_success:
                continue
            if trigger.recent_failure and not self.recent_mission_failure:
                continue
            
            # Check time of day
            if trigger.time_of_day_required and trigger.time_of_day_required != time_of_day:
                continue
            
            # Check required NPCs
            if trigger.npcs_required:
                if not all(npc in available_npcs for npc in trigger.npcs_required):
                    continue
            
            # Check if participants are available
            if not all(npc in available_npcs for npc in event.participants):
                continue
            
            triggered_events.append(event)
        
        # Return highest priority (most specific triggers)
        if triggered_events:
            # Priority: crisis > argument > celebration > meal > storytelling
            priority_order = [
                EventType.CRISIS_MEETING,
                EventType.ARGUMENT,
                EventType.MEMORIAL,
                EventType.CELEBRATION,
                EventType.MEAL,
                EventType.STORYTELLING,
                EventType.TRAINING,
                EventType.GAME_NIGHT,
            ]
            
            triggered_events.sort(
                key=lambda e: priority_order.index(e.event_type) if e.event_type in priority_order else 999
            )
            
            return triggered_events[0]
        
        return None
    
    def start_event(self, event_id: str) -> Optional[EventDialoguePart]:
        """
        Start a camp event.
        Returns the first dialogue part.
        """
        event = self.events.get(event_id)
        if not event:
            return None
        
        self.active_event = event
        self.current_event_part = 0
        event.last_triggered = self.current_hour
        
        if event.dialogue_parts:
            return event.dialogue_parts[0]
        return None
    
    def advance_event(self) -> Optional[EventDialoguePart]:
        """
        Advance to next part of active event.
        Returns next dialogue part or None if event complete.
        """
        if not self.active_event:
            return None
        
        self.current_event_part += 1
        
        if self.current_event_part < len(self.active_event.dialogue_parts):
            return self.active_event.dialogue_parts[self.current_event_part]
        else:
            # Event complete
            self.active_event = None
            self.current_event_part = 0
            return None
    
    def get_event_morale_effect(self) -> float:
        """Get morale effect of completed event."""
        if self.active_event:
            return self.active_event.morale_effect
        return 0.0
    
    def set_mission_result(self, success: bool) -> None:
        """Record a mission result for event triggering."""
        if success:
            self.recent_mission_success = True
            self.recent_mission_failure = False
        else:
            self.recent_mission_success = False
            self.recent_mission_failure = True
    
    def clear_mission_results(self) -> None:
        """Clear recent mission results (call after some time)."""
        self.recent_mission_success = False
        self.recent_mission_failure = False
    
    def to_dict(self) -> dict:
        """Serialize event manager state."""
        return {
            "current_hour": self.current_hour,
            "recent_mission_success": self.recent_mission_success,
            "recent_mission_failure": self.recent_mission_failure,
            "active_event": self.active_event.event_id if self.active_event else None,
            "current_event_part": self.current_event_part,
            "event_last_triggered": {
                event_id: event.last_triggered
                for event_id, event in self.events.items()
            }
        }
