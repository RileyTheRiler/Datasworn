"""
Daily Scripts & Lorebook System.
Time-based NPC schedules and keyword-activated lore retrieval.

Daily Scripts make NPCs feel like they have lives.
Lorebook ensures long-term narrative consistency.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import re


# ============================================================================
# Time System
# ============================================================================

class TimeOfDay(Enum):
    """Periods of the day."""
    DAWN = "dawn"  # 5-7
    MORNING = "morning"  # 7-12
    AFTERNOON = "afternoon"  # 12-17
    EVENING = "evening"  # 17-20
    NIGHT = "night"  # 20-24
    LATE_NIGHT = "late_night"  # 0-5


def get_time_of_day(hour: int) -> TimeOfDay:
    """Get time of day from hour (0-23)."""
    if 5 <= hour < 7:
        return TimeOfDay.DAWN
    elif 7 <= hour < 12:
        return TimeOfDay.MORNING
    elif 12 <= hour < 17:
        return TimeOfDay.AFTERNOON
    elif 17 <= hour < 20:
        return TimeOfDay.EVENING
    elif 20 <= hour < 24:
        return TimeOfDay.NIGHT
    else:
        return TimeOfDay.LATE_NIGHT


# ============================================================================
# Daily Scripts
# ============================================================================

@dataclass
class ScheduledActivity:
    """A single scheduled activity."""
    time_of_day: TimeOfDay
    activity: str
    location: str
    interruptible: bool = True
    dialogue_available: bool = True


@dataclass
class DailyScript:
    """A full daily schedule for an NPC."""
    npc_name: str
    schedule: dict[TimeOfDay, ScheduledActivity] = field(default_factory=dict)
    current_activity: ScheduledActivity | None = None
    
    def get_activity(self, hour: int) -> ScheduledActivity | None:
        """Get current activity based on hour."""
        time = get_time_of_day(hour)
        activity = self.schedule.get(time)
        self.current_activity = activity
        return activity
    
    def get_narrator_context(self, hour: int) -> str:
        """Generate context for narrator about NPC's schedule."""
        activity = self.get_activity(hour)
        if not activity:
            return f"[{self.npc_name}: No scheduled activity]"
        
        return (
            f"[SCHEDULE: {self.npc_name}]\n"
            f"Time: {activity.time_of_day.value}\n"
            f"Activity: {activity.activity}\n"
            f"Location: {activity.location}\n"
            f"Available for dialogue: {activity.dialogue_available}"
        )


# Pre-built schedule templates
SCHEDULE_TEMPLATES = {
    "worker": {
        TimeOfDay.DAWN: ScheduledActivity(TimeOfDay.DAWN, "waking up, preparing for day", "quarters"),
        TimeOfDay.MORNING: ScheduledActivity(TimeOfDay.MORNING, "working at station", "workplace"),
        TimeOfDay.AFTERNOON: ScheduledActivity(TimeOfDay.AFTERNOON, "working, taking break", "workplace"),
        TimeOfDay.EVENING: ScheduledActivity(TimeOfDay.EVENING, "relaxing, eating", "common area"),
        TimeOfDay.NIGHT: ScheduledActivity(TimeOfDay.NIGHT, "leisure time", "bar or quarters"),
        TimeOfDay.LATE_NIGHT: ScheduledActivity(TimeOfDay.LATE_NIGHT, "sleeping", "quarters", interruptible=False, dialogue_available=False),
    },
    "guard": {
        TimeOfDay.DAWN: ScheduledActivity(TimeOfDay.DAWN, "end of night shift, debriefing", "guard post"),
        TimeOfDay.MORNING: ScheduledActivity(TimeOfDay.MORNING, "off duty, sleeping", "quarters", interruptible=False, dialogue_available=False),
        TimeOfDay.AFTERNOON: ScheduledActivity(TimeOfDay.AFTERNOON, "off duty, personal time", "common area"),
        TimeOfDay.EVENING: ScheduledActivity(TimeOfDay.EVENING, "preparing for shift", "quarters"),
        TimeOfDay.NIGHT: ScheduledActivity(TimeOfDay.NIGHT, "on patrol", "patrol route"),
        TimeOfDay.LATE_NIGHT: ScheduledActivity(TimeOfDay.LATE_NIGHT, "on patrol, vigilant", "patrol route"),
    },
    "merchant": {
        TimeOfDay.DAWN: ScheduledActivity(TimeOfDay.DAWN, "opening shop, inventory check", "shop"),
        TimeOfDay.MORNING: ScheduledActivity(TimeOfDay.MORNING, "selling goods, busy", "shop"),
        TimeOfDay.AFTERNOON: ScheduledActivity(TimeOfDay.AFTERNOON, "slower sales, restocking", "shop"),
        TimeOfDay.EVENING: ScheduledActivity(TimeOfDay.EVENING, "closing shop, counting credits", "shop"),
        TimeOfDay.NIGHT: ScheduledActivity(TimeOfDay.NIGHT, "dinner, socializing", "bar"),
        TimeOfDay.LATE_NIGHT: ScheduledActivity(TimeOfDay.LATE_NIGHT, "sleeping", "quarters", interruptible=False, dialogue_available=False),
    },
    "criminal": {
        TimeOfDay.DAWN: ScheduledActivity(TimeOfDay.DAWN, "returning from job, laying low", "hideout"),
        TimeOfDay.MORNING: ScheduledActivity(TimeOfDay.MORNING, "sleeping", "hideout", interruptible=False, dialogue_available=False),
        TimeOfDay.AFTERNOON: ScheduledActivity(TimeOfDay.AFTERNOON, "waking, planning", "hideout"),
        TimeOfDay.EVENING: ScheduledActivity(TimeOfDay.EVENING, "meeting contacts", "bar"),
        TimeOfDay.NIGHT: ScheduledActivity(TimeOfDay.NIGHT, "working a job", "various", interruptible=False),
        TimeOfDay.LATE_NIGHT: ScheduledActivity(TimeOfDay.LATE_NIGHT, "still working", "various", interruptible=False),
    },
}


class DailyScriptManager:
    """Manages daily scripts for all NPCs."""
    
    def __init__(self):
        self.scripts: dict[str, DailyScript] = {}
        self.current_hour: int = 12
    
    def create_script(
        self,
        npc_name: str,
        template: str = "worker",
    ) -> DailyScript:
        """Create a daily script from template."""
        script = DailyScript(npc_name=npc_name)
        
        template_schedule = SCHEDULE_TEMPLATES.get(template, SCHEDULE_TEMPLATES["worker"])
        script.schedule = template_schedule.copy()
        
        self.scripts[npc_name] = script
        return script
    
    def advance_time(self, hours: int = 1) -> None:
        """Advance the current hour."""
        self.current_hour = (self.current_hour + hours) % 24
    
    def get_all_activities(self) -> dict[str, ScheduledActivity | None]:
        """Get current activities for all NPCs."""
        return {
            name: script.get_activity(self.current_hour)
            for name, script in self.scripts.items()
        }
    
    def get_narrator_context(self) -> str:
        """Generate context for narrator about current NPC activities."""
        lines = [f"[WORLD TIME: {self.current_hour:02d}:00 - {get_time_of_day(self.current_hour).value.upper()}]"]
        
        for name, script in list(self.scripts.items())[:5]:
            activity = script.get_activity(self.current_hour)
            if activity:
                lines.append(f"• {name}: {activity.activity} @ {activity.location}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "current_hour": self.current_hour,
            "scripts": {
                name: {
                    "npc_name": script.npc_name,
                    "current_activity": script.current_activity.activity if script.current_activity else None,
                }
                for name, script in self.scripts.items()
            },
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DailyScriptManager":
        manager = cls()
        manager.current_hour = data.get("current_hour", 12)
        # Scripts would need to be recreated from templates
        return manager


# ============================================================================
# Lorebook System (Keyword-Activated Retrieval)
# ============================================================================

@dataclass
class LorebookEntry:
    """A single lorebook entry."""
    id: str
    title: str
    content: str
    keywords: list[str]
    category: str = "general"
    priority: int = 5  # 1-10, higher = more important
    last_accessed: int = 0  # Scene number
    access_count: int = 0


class Lorebook:
    """
    Keyword-activated lore retrieval system.
    Ensures narrative consistency for important entities.
    """
    
    def __init__(self):
        self.entries: dict[str, LorebookEntry] = {}
        self.keyword_index: dict[str, list[str]] = {}  # keyword -> entry_ids
        self.current_scene: int = 0
    
    def add_entry(
        self,
        id: str,
        title: str,
        content: str,
        keywords: list[str],
        category: str = "general",
        priority: int = 5,
    ) -> LorebookEntry:
        """Add a lorebook entry."""
        entry = LorebookEntry(
            id=id,
            title=title,
            content=content,
            keywords=[k.lower() for k in keywords],
            category=category,
            priority=priority,
        )
        
        self.entries[id] = entry
        
        # Index keywords
        for keyword in entry.keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = []
            self.keyword_index[keyword].append(id)
        
        return entry
    
    def search(self, text: str, max_results: int = 3) -> list[LorebookEntry]:
        """Search for relevant entries based on text."""
        text_lower = text.lower()
        matches: dict[str, int] = {}  # entry_id -> score
        
        # Check each keyword
        for keyword, entry_ids in self.keyword_index.items():
            if keyword in text_lower:
                for eid in entry_ids:
                    matches[eid] = matches.get(eid, 0) + 1
        
        # Score and sort
        scored = []
        for eid, keyword_matches in matches.items():
            entry = self.entries[eid]
            score = keyword_matches * 2 + entry.priority
            scored.append((entry, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Update access stats
        results = []
        for entry, score in scored[:max_results]:
            entry.last_accessed = self.current_scene
            entry.access_count += 1
            results.append(entry)
        
        return results
    
    def get_entry(self, id: str) -> LorebookEntry | None:
        """Get a specific entry by ID."""
        return self.entries.get(id)
    
    def get_context_for_input(self, player_input: str) -> str:
        """Get lorebook context for player input."""
        matches = self.search(player_input)
        
        if not matches:
            return ""
        
        lines = ["[LOREBOOK RECALL]"]
        for entry in matches:
            lines.append(f"\n{entry.title.upper()}:")
            lines.append(entry.content)
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "entries": {
                eid: {
                    "id": e.id,
                    "title": e.title,
                    "content": e.content,
                    "keywords": e.keywords,
                    "category": e.category,
                    "priority": e.priority,
                    "last_accessed": e.last_accessed,
                    "access_count": e.access_count,
                }
                for eid, e in self.entries.items()
            },
            "current_scene": self.current_scene,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Lorebook":
        lorebook = cls()
        lorebook.current_scene = data.get("current_scene", 0)
        
        for eid, edata in data.get("entries", {}).items():
            entry = LorebookEntry(
                id=edata.get("id", eid),
                title=edata.get("title", ""),
                content=edata.get("content", ""),
                keywords=edata.get("keywords", []),
                category=edata.get("category", "general"),
                priority=edata.get("priority", 5),
                last_accessed=edata.get("last_accessed", 0),
                access_count=edata.get("access_count", 0),
            )
            lorebook.entries[eid] = entry
            
            # Rebuild keyword index
            for keyword in entry.keywords:
                if keyword not in lorebook.keyword_index:
                    lorebook.keyword_index[keyword] = []
                lorebook.keyword_index[keyword].append(eid)
        
        return lorebook


# ============================================================================
# Progressive Summarization
# ============================================================================

class ProgressiveSummarizer:
    """
    Manages context window through progressive summarization.
    Recent content is verbatim, older content is compressed.
    """
    
    def __init__(self, verbatim_paragraphs: int = 5):
        self.verbatim_paragraphs = verbatim_paragraphs
        self.verbatim_content: list[str] = []
        self.summaries: list[str] = []
        self.key_events: list[str] = []  # Always preserved
    
    def add_content(self, content: str) -> None:
        """Add new content, managing window size."""
        self.verbatim_content.append(content)
        
        # Compress oldest if over limit
        if len(self.verbatim_content) > self.verbatim_paragraphs:
            oldest = self.verbatim_content.pop(0)
            # Simple summarization (would use LLM in production)
            summary = self._simple_summarize(oldest)
            self.summaries.append(summary)
            
            # Keep summaries limited too
            if len(self.summaries) > 10:
                self.summaries = self.summaries[-10:]
    
    def add_key_event(self, event: str) -> None:
        """Add a key event that should never be forgotten."""
        self.key_events.append(event)
        if len(self.key_events) > 20:
            self.key_events = self.key_events[-20:]
    
    def _simple_summarize(self, text: str) -> str:
        """Simple summarization (placeholder for LLM)."""
        # Extract first sentence or truncate
        sentences = text.split('.')
        if sentences:
            return sentences[0][:100] + "..."
        return text[:100] + "..."
    
    def get_context(self) -> str:
        """Get full context for LLM."""
        lines = []
        
        if self.key_events:
            lines.append("[KEY EVENTS]")
            for event in self.key_events[-5:]:
                lines.append(f"• {event}")
        
        if self.summaries:
            lines.append("\n[EARLIER SUMMARY]")
            for summary in self.summaries[-3:]:
                lines.append(summary)
        
        if self.verbatim_content:
            lines.append("\n[RECENT EVENTS]")
            for content in self.verbatim_content:
                lines.append(content)
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "verbatim_content": self.verbatim_content,
            "summaries": self.summaries,
            "key_events": self.key_events,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProgressiveSummarizer":
        summarizer = cls()
        summarizer.verbatim_content = data.get("verbatim_content", [])
        summarizer.summaries = data.get("summaries", [])
        summarizer.key_events = data.get("key_events", [])
        return summarizer


# ============================================================================
# Convenience Functions
# ============================================================================

def create_lorebook() -> Lorebook:
    """Create a new lorebook."""
    return Lorebook()


def create_daily_script_manager() -> DailyScriptManager:
    """Create a new daily script manager."""
    return DailyScriptManager()


def quick_lore_search(lorebook: Lorebook, text: str) -> str:
    """Quick lorebook search."""
    return lorebook.get_context_for_input(text)
