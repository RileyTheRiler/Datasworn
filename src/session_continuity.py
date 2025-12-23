"""
Session Continuity - Generate recaps and cliffhangers for session breaks.
Helps players maintain narrative momentum across play sessions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime

from src.logging_config import get_logger

logger = get_logger("session")


@dataclass
class SessionEvent:
    """A notable event from the session."""
    description: str
    event_type: str  # "roll", "decision", "discovery", "npc", "vow"
    importance: float  # 0.0 to 1.0
    turn_number: int
    related_entities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "event_type": self.event_type,
            "importance": self.importance,
            "turn_number": self.turn_number,
            "related_entities": self.related_entities,
        }


@dataclass
class SessionSummary:
    """Summary of a play session."""
    session_id: str
    start_time: str
    end_time: str
    turn_count: int
    major_events: list[SessionEvent]
    vow_changes: list[dict[str, Any]]
    npcs_encountered: list[str]
    locations_visited: list[str]
    cliffhanger: str
    mood: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "turn_count": self.turn_count,
            "major_events": [e.to_dict() for e in self.major_events],
            "vow_changes": self.vow_changes,
            "npcs_encountered": self.npcs_encountered,
            "locations_visited": self.locations_visited,
            "cliffhanger": self.cliffhanger,
            "mood": self.mood,
        }


@dataclass
class SessionTracker:
    """Tracks events during a session for recap generation."""
    events: list[SessionEvent] = field(default_factory=list)
    npcs_encountered: list[str] = field(default_factory=list)
    locations_visited: list[str] = field(default_factory=list)
    vow_changes: list[dict[str, Any]] = field(default_factory=list)
    current_turn: int = 0
    session_start: str = ""
    last_narrative: str = ""
    tension_high_point: float = 0.0
    current_location: str = ""

    def __post_init__(self):
        if not self.session_start:
            self.session_start = datetime.now().isoformat()

    def record_event(
        self,
        description: str,
        event_type: str,
        importance: float = 0.5,
        related_entities: Optional[list[str]] = None,
    ) -> None:
        """Record a notable event."""
        event = SessionEvent(
            description=description,
            event_type=event_type,
            importance=importance,
            turn_number=self.current_turn,
            related_entities=related_entities or [],
        )
        self.events.append(event)
        logger.debug(f"Recorded event: {description} ({event_type})")

    def record_roll(self, move_name: str, outcome: str, context: str) -> None:
        """Record a dice roll result."""
        importance = 0.3
        if outcome == "miss":
            importance = 0.7
        elif outcome == "strong_hit" and "match" in context.lower():
            importance = 0.8

        self.record_event(
            description=f"{move_name}: {outcome.replace('_', ' ').title()}",
            event_type="roll",
            importance=importance,
        )

    def record_npc_encounter(self, npc_name: str) -> None:
        """Record an NPC encounter."""
        if npc_name not in self.npcs_encountered:
            self.npcs_encountered.append(npc_name)
            self.record_event(
                description=f"Encountered {npc_name}",
                event_type="npc",
                importance=0.5,
                related_entities=[npc_name],
            )

    def record_location_visit(self, location: str) -> None:
        """Record visiting a new location."""
        if location != self.current_location:
            self.current_location = location
            if location not in self.locations_visited:
                self.locations_visited.append(location)
                self.record_event(
                    description=f"Arrived at {location}",
                    event_type="discovery",
                    importance=0.4,
                )

    def record_vow_change(
        self,
        vow_name: str,
        change_type: str,  # "progress", "sworn", "fulfilled", "forsaken"
        old_progress: int = 0,
        new_progress: int = 0,
    ) -> None:
        """Record a vow state change."""
        change = {
            "vow_name": vow_name,
            "change_type": change_type,
            "old_progress": old_progress,
            "new_progress": new_progress,
            "turn": self.current_turn,
        }
        self.vow_changes.append(change)

        importance = 0.6
        if change_type in ["fulfilled", "forsaken"]:
            importance = 1.0
        elif change_type == "sworn":
            importance = 0.8

        self.record_event(
            description=f"Vow '{vow_name}': {change_type}",
            event_type="vow",
            importance=importance,
        )

    def record_tension(self, tension_level: float) -> None:
        """Track tension levels for mood analysis."""
        if tension_level > self.tension_high_point:
            self.tension_high_point = tension_level

    def advance_turn(self) -> None:
        """Advance the turn counter."""
        self.current_turn += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "events": [e.to_dict() for e in self.events],
            "npcs_encountered": self.npcs_encountered,
            "locations_visited": self.locations_visited,
            "vow_changes": self.vow_changes,
            "current_turn": self.current_turn,
            "session_start": self.session_start,
            "last_narrative": self.last_narrative,
            "tension_high_point": self.tension_high_point,
            "current_location": self.current_location,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionTracker":
        migrated = cls._migrate_payload(dict(data))

        tracker = cls(
            npcs_encountered=migrated.get("npcs_encountered", []),
            locations_visited=migrated.get("locations_visited", []),
            vow_changes=migrated.get("vow_changes", []),
            current_turn=migrated.get("current_turn", 0),
            session_start=migrated.get("session_start", ""),
            last_narrative=migrated.get("last_narrative", ""),
            tension_high_point=migrated.get("tension_high_point", 0.0),
            current_location=migrated.get("current_location", ""),
        )
        for e_data in migrated.get("events", []):
            tracker.events.append(SessionEvent(
                description=e_data.get("description", ""),
                event_type=e_data.get("event_type", "event"),
                importance=e_data.get("importance", 0.5),
                turn_number=e_data.get("turn_number", 0),
                related_entities=e_data.get("related_entities", []),
            ))
        return tracker

    @staticmethod
    def _migrate_payload(data: dict[str, Any]) -> dict[str, Any]:
        version = data.get("schema_version", 0)
        if version < 1:
            data.setdefault("events", [])
            data.setdefault("npcs_encountered", [])
            data.setdefault("locations_visited", [])
            data.setdefault("vow_changes", [])
            data.setdefault("current_turn", 0)
            data.setdefault("session_start", datetime.now().isoformat())
            data.setdefault("last_narrative", "")
            data.setdefault("tension_high_point", 0.0)
            data.setdefault("current_location", "")
        data["schema_version"] = 1
        return data


def generate_session_recap(tracker: SessionTracker) -> str:
    """
    Generate a "Previously on..." style recap.

    Args:
        tracker: SessionTracker with session data

    Returns:
        Formatted recap string
    """
    if not tracker.events:
        return "This is a new adventure. The path ahead awaits."

    # Get major events (importance > 0.5)
    major_events = sorted(
        [e for e in tracker.events if e.importance > 0.5],
        key=lambda x: x.importance,
        reverse=True,
    )[:5]

    lines = ["**Previously...**\n"]

    # Summarize by event type
    vow_events = [e for e in major_events if e.event_type == "vow"]
    roll_events = [e for e in major_events if e.event_type == "roll"]
    other_events = [e for e in major_events if e.event_type not in ["vow", "roll"]]

    if vow_events:
        lines.append("*Oaths:*")
        for e in vow_events[:2]:
            lines.append(f"  • {e.description}")
        lines.append("")

    if roll_events:
        notable_rolls = [e for e in roll_events if e.importance >= 0.7]
        if notable_rolls:
            lines.append("*Critical Moments:*")
            for e in notable_rolls[:2]:
                lines.append(f"  • {e.description}")
            lines.append("")

    if other_events:
        lines.append("*Events:*")
        for e in other_events[:3]:
            lines.append(f"  • {e.description}")
        lines.append("")

    # NPCs and locations
    if tracker.npcs_encountered:
        lines.append(f"*Characters encountered:* {', '.join(tracker.npcs_encountered[:5])}")

    if tracker.locations_visited:
        lines.append(f"*Places explored:* {', '.join(tracker.locations_visited[:5])}")

    # Current situation
    if tracker.current_location:
        lines.append(f"\n*Currently:* {tracker.current_location}")

    return "\n".join(lines)


def generate_cliffhanger(
    tracker: SessionTracker,
    current_narrative: str,
    tension_level: float,
) -> str:
    """
    Generate a cliffhanger for session end.

    Args:
        tracker: SessionTracker with session data
        current_narrative: The last narrative text
        tension_level: Current tension (0.0 to 1.0)

    Returns:
        Cliffhanger text
    """
    # Extract potential hooks from recent events
    recent_events = [e for e in tracker.events[-5:] if e.importance > 0.4]

    # High tension cliffhangers
    if tension_level >= 0.7:
        hooks = [
            "The danger is far from over...",
            "What comes next will test everything...",
            "The moment of truth approaches...",
            "There's no turning back now...",
        ]
    elif tension_level >= 0.4:
        hooks = [
            "Questions remain unanswered...",
            "The path ahead grows uncertain...",
            "New challenges await...",
            "The journey continues...",
        ]
    else:
        hooks = [
            "A moment of calm before the storm...",
            "Time to prepare for what's to come...",
            "The adventure is just beginning...",
            "Rest while you can...",
        ]

    # Pick based on recent events
    import random
    random.seed(tracker.current_turn)
    base_hook = random.choice(hooks)

    # Add context from unresolved vows
    active_vows = [
        v for v in tracker.vow_changes
        if v["change_type"] not in ["fulfilled", "forsaken"]
    ]
    if active_vows:
        recent_vow = active_vows[-1]
        return f"{base_hook}\n\n*Your oath weighs heavy: {recent_vow['vow_name']}*"

    return base_hook


def generate_session_summary(tracker: SessionTracker) -> SessionSummary:
    """
    Generate a complete session summary.

    Args:
        tracker: SessionTracker with session data

    Returns:
        SessionSummary object
    """
    import uuid

    # Determine mood from events and tension
    if tracker.tension_high_point >= 0.8:
        mood = "intense"
    elif tracker.tension_high_point >= 0.5:
        mood = "dramatic"
    elif len(tracker.events) < 5:
        mood = "exploratory"
    else:
        mood = "steady"

    # Get major events
    major_events = sorted(
        [e for e in tracker.events if e.importance > 0.5],
        key=lambda x: x.importance,
        reverse=True,
    )[:10]

    return SessionSummary(
        session_id=str(uuid.uuid4())[:8],
        start_time=tracker.session_start,
        end_time=datetime.now().isoformat(),
        turn_count=tracker.current_turn,
        major_events=major_events,
        vow_changes=tracker.vow_changes,
        npcs_encountered=tracker.npcs_encountered,
        locations_visited=tracker.locations_visited,
        cliffhanger=generate_cliffhanger(tracker, tracker.last_narrative, tracker.tension_high_point),
        mood=mood,
    )


def format_session_end_screen(summary: SessionSummary) -> str:
    """
    Format the session end screen for display.

    Args:
        summary: SessionSummary object

    Returns:
        Formatted end screen text
    """
    lines = [
        "═" * 50,
        "        SESSION COMPLETE",
        "═" * 50,
        "",
        f"⏱ Duration: {summary.turn_count} turns",
        f"🎭 Mood: {summary.mood.title()}",
        "",
    ]

    if summary.major_events:
        lines.append("📖 **Highlights:**")
        for event in summary.major_events[:5]:
            icon = {
                "vow": "⚔",
                "roll": "🎲",
                "npc": "👤",
                "discovery": "🔍",
            }.get(event.event_type, "•")
            lines.append(f"  {icon} {event.description}")
        lines.append("")

    if summary.vow_changes:
        lines.append("⚔ **Oath Progress:**")
        for change in summary.vow_changes[-3:]:
            lines.append(f"  • {change['vow_name']}: {change['change_type']}")
        lines.append("")

    lines.extend([
        "─" * 50,
        "",
        summary.cliffhanger,
        "",
        "─" * 50,
        "*Your progress has been saved.*",
        "*Until next time, Traveler...*",
    ])

    return "\n".join(lines)
