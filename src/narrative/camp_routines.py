"""
Camp Character Routines.

Extends the daily scripts system with camp-specific routines, intent tags,
and weather/season variants for all crew members.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.daily_scripts import TimeOfDay, ScheduledActivity


class IntentTag(Enum):
    """Intent behind an NPC's activity."""
    WORK = "work"
    SOCIAL = "social"
    PERFORM = "perform"
    REST = "rest"
    MAINTENANCE = "maintenance"
    PERSONAL = "personal"


class Weather(Enum):
    """Weather conditions that affect routines."""
    CLEAR = "clear"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"


class Season(Enum):
    """Seasonal variants."""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


@dataclass
class CampActivity(ScheduledActivity):
    """Extended scheduled activity with camp-specific features."""
    intent: IntentTag = IntentTag.PERSONAL
    shared_event_eligible: bool = True
    weather_override: dict[Weather, str] = field(default_factory=dict)  # Weather -> alternate activity
    season_override: dict[Season, str] = field(default_factory=dict)  # Season -> alternate activity
    
    def get_activity_for_conditions(
        self,
        weather: Weather = Weather.CLEAR,
        season: Season = Season.SUMMER
    ) -> str:
        """Get activity description adjusted for weather/season."""
        # Weather takes priority
        if weather in self.weather_override:
            return self.weather_override[weather]
        
        # Then season
        if season in self.season_override:
            return self.season_override[season]
        
        # Default
        return self.activity


@dataclass
class CampRoutine:
    """Complete daily routine for a camp character."""
    npc_id: str
    npc_name: str
    schedule: dict[TimeOfDay, CampActivity] = field(default_factory=dict)
    
    def get_activity(
        self,
        hour: int,
        weather: Weather = Weather.CLEAR,
        season: Season = Season.SUMMER
    ) -> Optional[CampActivity]:
        """Get current activity based on time and conditions."""
        from src.daily_scripts import get_time_of_day
        time = get_time_of_day(hour)
        activity = self.schedule.get(time)
        return activity
    
    def to_dict(self) -> dict:
        return {
            "npc_id": self.npc_id,
            "npc_name": self.npc_name,
            "schedule": {
                time.value: {
                    "activity": act.activity,
                    "location": act.location,
                    "intent": act.intent.value,
                    "interruptible": act.interruptible,
                    "dialogue_available": act.dialogue_available,
                }
                for time, act in self.schedule.items()
            }
        }


# =============================================================================
# CREW MEMBER ROUTINES
# =============================================================================

CAMP_CHARACTER_ROUTINES = {
    "yuki": CampRoutine(
        npc_id="yuki",
        npc_name="Yuki",
        schedule={
            TimeOfDay.DAWN: CampActivity(
                time_of_day=TimeOfDay.DAWN,
                activity="running perimeter check",
                location="lookout_point",
                intent=IntentTag.WORK,
                interruptible=False,
                dialogue_available=False,
                weather_override={
                    Weather.RAIN: "checking security systems from workshop",
                    Weather.STORM: "monitoring alerts from sleeping quarters",
                }
            ),
            TimeOfDay.MORNING: CampActivity(
                time_of_day=TimeOfDay.MORNING,
                activity="reviewing security logs, drinking coffee",
                location="common_area",
                intent=IntentTag.WORK,
                shared_event_eligible=True,
            ),
            TimeOfDay.AFTERNOON: CampActivity(
                time_of_day=TimeOfDay.AFTERNOON,
                activity="training drills, maintaining weapons",
                location="supply_area",
                intent=IntentTag.MAINTENANCE,
                weather_override={
                    Weather.RAIN: "cleaning weapons in workshop",
                }
            ),
            TimeOfDay.EVENING: CampActivity(
                time_of_day=TimeOfDay.EVENING,
                activity="sitting by the fire, watchful",
                location="common_area",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.NIGHT: CampActivity(
                time_of_day=TimeOfDay.NIGHT,
                activity="on patrol, alert",
                location="lookout_point",
                intent=IntentTag.WORK,
                interruptible=False,
                dialogue_available=True,  # Can talk while on watch
            ),
            TimeOfDay.LATE_NIGHT: CampActivity(
                time_of_day=TimeOfDay.LATE_NIGHT,
                activity="light sleep, ready to wake",
                location="sleeping_quarters",
                intent=IntentTag.REST,
                interruptible=True,  # Yuki is always on alert
                dialogue_available=False,
            ),
        }
    ),
    
    "torres": CampRoutine(
        npc_id="torres",
        npc_name="Torres",
        schedule={
            TimeOfDay.DAWN: CampActivity(
                time_of_day=TimeOfDay.DAWN,
                activity="watching the sunrise, planning routes",
                location="lookout_point",
                intent=IntentTag.PERSONAL,
            ),
            TimeOfDay.MORNING: CampActivity(
                time_of_day=TimeOfDay.MORNING,
                activity="reviewing navigation charts",
                location="workshop",
                intent=IntentTag.WORK,
            ),
            TimeOfDay.AFTERNOON: CampActivity(
                time_of_day=TimeOfDay.AFTERNOON,
                activity="helping with repairs, telling stories",
                location="workshop",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.EVENING: CampActivity(
                time_of_day=TimeOfDay.EVENING,
                activity="cooking dinner, sharing tales",
                location="common_area",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
                weather_override={
                    Weather.RAIN: "cooking inside, rain drumming on roof",
                }
            ),
            TimeOfDay.NIGHT: CampActivity(
                time_of_day=TimeOfDay.NIGHT,
                activity="playing cards, relaxing",
                location="common_area",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.LATE_NIGHT: CampActivity(
                time_of_day=TimeOfDay.LATE_NIGHT,
                activity="sleeping soundly",
                location="sleeping_quarters",
                intent=IntentTag.REST,
                interruptible=False,
                dialogue_available=False,
            ),
        }
    ),
    
    "kai": CampRoutine(
        npc_id="kai",
        npc_name="Kai",
        schedule={
            TimeOfDay.DAWN: CampActivity(
                time_of_day=TimeOfDay.DAWN,
                activity="tending to small garden",
                location="meditation_spot",
                intent=IntentTag.PERSONAL,
                season_override={
                    Season.WINTER: "checking heating systems",
                }
            ),
            TimeOfDay.MORNING: CampActivity(
                time_of_day=TimeOfDay.MORNING,
                activity="working on ship systems",
                location="workshop",
                intent=IntentTag.WORK,
            ),
            TimeOfDay.AFTERNOON: CampActivity(
                time_of_day=TimeOfDay.AFTERNOON,
                activity="deep in repairs, focused",
                location="workshop",
                intent=IntentTag.WORK,
                interruptible=False,
            ),
            TimeOfDay.EVENING: CampActivity(
                time_of_day=TimeOfDay.EVENING,
                activity="quiet conversation by the fire",
                location="common_area",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.NIGHT: CampActivity(
                time_of_day=TimeOfDay.NIGHT,
                activity="reading technical manuals",
                location="sleeping_quarters",
                intent=IntentTag.PERSONAL,
            ),
            TimeOfDay.LATE_NIGHT: CampActivity(
                time_of_day=TimeOfDay.LATE_NIGHT,
                activity="sleeping",
                location="sleeping_quarters",
                intent=IntentTag.REST,
                interruptible=False,
                dialogue_available=False,
            ),
        }
    ),
    
    "okonkwo": CampRoutine(
        npc_id="okonkwo",
        npc_name="Dr. Okonkwo",
        schedule={
            TimeOfDay.DAWN: CampActivity(
                time_of_day=TimeOfDay.DAWN,
                activity="morning meditation",
                location="meditation_spot",
                intent=IntentTag.PERSONAL,
            ),
            TimeOfDay.MORNING: CampActivity(
                time_of_day=TimeOfDay.MORNING,
                activity="checking medical supplies",
                location="supply_area",
                intent=IntentTag.WORK,
            ),
            TimeOfDay.AFTERNOON: CampActivity(
                time_of_day=TimeOfDay.AFTERNOON,
                activity="writing in journal, observing crew",
                location="common_area",
                intent=IntentTag.PERSONAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.EVENING: CampActivity(
                time_of_day=TimeOfDay.EVENING,
                activity="preparing tea, offering counsel",
                location="common_area",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.NIGHT: CampActivity(
                time_of_day=TimeOfDay.NIGHT,
                activity="reading, available if needed",
                location="sleeping_quarters",
                intent=IntentTag.PERSONAL,
                dialogue_available=True,
            ),
            TimeOfDay.LATE_NIGHT: CampActivity(
                time_of_day=TimeOfDay.LATE_NIGHT,
                activity="sleeping lightly",
                location="sleeping_quarters",
                intent=IntentTag.REST,
                interruptible=True,  # Doctor is always on call
                dialogue_available=False,
            ),
        }
    ),
    
    "vasquez": CampRoutine(
        npc_id="vasquez",
        npc_name="Vasquez",
        schedule={
            TimeOfDay.DAWN: CampActivity(
                time_of_day=TimeOfDay.DAWN,
                activity="organizing supplies",
                location="supply_area",
                intent=IntentTag.WORK,
            ),
            TimeOfDay.MORNING: CampActivity(
                time_of_day=TimeOfDay.MORNING,
                activity="inventory management",
                location="supply_area",
                intent=IntentTag.WORK,
            ),
            TimeOfDay.AFTERNOON: CampActivity(
                time_of_day=TimeOfDay.AFTERNOON,
                activity="trading stories, checking manifests",
                location="common_area",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.EVENING: CampActivity(
                time_of_day=TimeOfDay.EVENING,
                activity="gambling, laughing",
                location="common_area",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.NIGHT: CampActivity(
                time_of_day=TimeOfDay.NIGHT,
                activity="having a drink, winding down",
                location="common_area",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.LATE_NIGHT: CampActivity(
                time_of_day=TimeOfDay.LATE_NIGHT,
                activity="sleeping",
                location="sleeping_quarters",
                intent=IntentTag.REST,
                interruptible=False,
                dialogue_available=False,
            ),
        }
    ),
    
    "ember": CampRoutine(
        npc_id="ember",
        npc_name="Ember",
        schedule={
            TimeOfDay.DAWN: CampActivity(
                time_of_day=TimeOfDay.DAWN,
                activity="sketching the sunrise",
                location="lookout_point",
                intent=IntentTag.PERSONAL,
            ),
            TimeOfDay.MORNING: CampActivity(
                time_of_day=TimeOfDay.MORNING,
                activity="helping with chores, learning",
                location="common_area",
                intent=IntentTag.WORK,
                shared_event_eligible=True,
            ),
            TimeOfDay.AFTERNOON: CampActivity(
                time_of_day=TimeOfDay.AFTERNOON,
                activity="practicing skills, asking questions",
                location="workshop",
                intent=IntentTag.WORK,
            ),
            TimeOfDay.EVENING: CampActivity(
                time_of_day=TimeOfDay.EVENING,
                activity="listening to stories by the fire",
                location="common_area",
                intent=IntentTag.SOCIAL,
                shared_event_eligible=True,
            ),
            TimeOfDay.NIGHT: CampActivity(
                time_of_day=TimeOfDay.NIGHT,
                activity="drawing, reflecting on the day",
                location="sleeping_quarters",
                intent=IntentTag.PERSONAL,
            ),
            TimeOfDay.LATE_NIGHT: CampActivity(
                time_of_day=TimeOfDay.LATE_NIGHT,
                activity="sleeping, sometimes nightmares",
                location="sleeping_quarters",
                intent=IntentTag.REST,
                interruptible=False,
                dialogue_available=False,
            ),
        }
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_routine(npc_id: str) -> Optional[CampRoutine]:
    """Get a character's camp routine."""
    return CAMP_CHARACTER_ROUTINES.get(npc_id)


def get_all_routines() -> dict[str, CampRoutine]:
    """Get all camp character routines."""
    return CAMP_CHARACTER_ROUTINES


def get_current_activities(
    hour: int,
    weather: Weather = Weather.CLEAR,
    season: Season = Season.SUMMER
) -> dict[str, CampActivity]:
    """Get current activities for all NPCs."""
    activities = {}
    for npc_id, routine in CAMP_CHARACTER_ROUTINES.items():
        activity = routine.get_activity(hour, weather, season)
        if activity:
            activities[npc_id] = activity
    return activities


def get_npcs_at_location(
    location: str,
    hour: int,
    weather: Weather = Weather.CLEAR,
    season: Season = Season.SUMMER
) -> list[str]:
    """Get list of NPC IDs currently at a specific location."""
    npcs = []
    for npc_id, routine in CAMP_CHARACTER_ROUTINES.items():
        activity = routine.get_activity(hour, weather, season)
        if activity and activity.location == location:
            npcs.append(npc_id)
    return npcs


def get_npcs_available_for_dialogue(
    hour: int,
    weather: Weather = Weather.CLEAR,
    season: Season = Season.SUMMER
) -> list[str]:
    """Get NPCs currently available for dialogue."""
    available = []
    for npc_id, routine in CAMP_CHARACTER_ROUTINES.items():
        activity = routine.get_activity(hour, weather, season)
        if activity and activity.dialogue_available:
            available.append(npc_id)
    return available


def get_npcs_for_shared_event(
    hour: int,
    weather: Weather = Weather.CLEAR,
    season: Season = Season.SUMMER
) -> list[str]:
    """Get NPCs eligible for shared events at current time."""
    eligible = []
    for npc_id, routine in CAMP_CHARACTER_ROUTINES.items():
        activity = routine.get_activity(hour, weather, season)
        if activity and activity.shared_event_eligible:
            eligible.append(npc_id)
    return eligible
