"""
Session Recap Generation System

Generates "Previously on..." summaries at session start using LLM.
Creates dramatic, engaging recaps of previous session events to
remind players of important story beats and set the mood.

Also generates campaign summaries and "story so far" synopses.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import random


class RecapStyle(Enum):
    """Style of recap narration."""
    DRAMATIC = "dramatic"  # Epic, cinematic style
    NOIR = "noir"  # Hard-boiled detective style
    MYSTERIOUS = "mysterious"  # Atmospheric, questions-raising
    URGENT = "urgent"  # Action-focused, high stakes
    REFLECTIVE = "reflective"  # Character-focused, emotional


@dataclass
class SessionEvent:
    """A significant event from a session."""
    description: str
    importance: int = 5  # 1-10
    characters_involved: List[str] = field(default_factory=list)
    location: str = ""
    is_cliffhanger: bool = False
    emotional_tone: str = ""  # e.g., "tense", "triumphant", "tragic"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "importance": self.importance,
            "characters_involved": self.characters_involved,
            "location": self.location,
            "is_cliffhanger": self.is_cliffhanger,
            "emotional_tone": self.emotional_tone,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionEvent":
        return cls(
            description=data.get("description", ""),
            importance=data.get("importance", 5),
            characters_involved=data.get("characters_involved", []),
            location=data.get("location", ""),
            is_cliffhanger=data.get("is_cliffhanger", False),
            emotional_tone=data.get("emotional_tone", ""),
        )


@dataclass
class SessionSummary:
    """Summary of a single session."""
    session_number: int
    events: List[SessionEvent] = field(default_factory=list)
    major_decisions: List[str] = field(default_factory=list)
    npcs_met: List[str] = field(default_factory=list)
    locations_visited: List[str] = field(default_factory=list)
    vow_progress: Dict[str, float] = field(default_factory=dict)  # vow_name -> progress
    cliffhanger: Optional[str] = None
    overall_tone: str = ""
    one_line_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_number": self.session_number,
            "events": [e.to_dict() for e in self.events],
            "major_decisions": self.major_decisions,
            "npcs_met": self.npcs_met,
            "locations_visited": self.locations_visited,
            "vow_progress": self.vow_progress,
            "cliffhanger": self.cliffhanger,
            "overall_tone": self.overall_tone,
            "one_line_summary": self.one_line_summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionSummary":
        return cls(
            session_number=data.get("session_number", 0),
            events=[SessionEvent.from_dict(e) for e in data.get("events", [])],
            major_decisions=data.get("major_decisions", []),
            npcs_met=data.get("npcs_met", []),
            locations_visited=data.get("locations_visited", []),
            vow_progress=data.get("vow_progress", {}),
            cliffhanger=data.get("cliffhanger"),
            overall_tone=data.get("overall_tone", ""),
            one_line_summary=data.get("one_line_summary", ""),
        )


class SessionRecapEngine:
    """
    Engine for generating session recaps and campaign summaries.

    Features:
    - LLM-powered dramatic recaps
    - Multiple recap styles
    - Event importance weighting
    - Cliffhanger emphasis
    - "Story so far" generation
    """

    RECAP_PROMPT = '''Generate a dramatic "Previously on..." style recap for a sci-fi RPG session.

PREVIOUS SESSION EVENTS (in order of importance):
{events}

MAJOR DECISIONS MADE:
{decisions}

KEY CHARACTERS INVOLVED:
{characters}

LOCATIONS VISITED:
{locations}

{cliffhanger_section}

STYLE: {style}

Generate a {length} recap in second person ("You...").
Focus on:
1. The most dramatic moments
2. Unresolved tensions
3. Character relationships
4. The cliffhanger (if any)

Make it cinematic and engaging, like a TV show "previously on" segment.
Use present tense for immediacy.

OUTPUT ONLY THE RECAP TEXT, no headers or meta-commentary:'''

    SUMMARY_PROMPT = '''Generate a one-paragraph "story so far" summary for a sci-fi RPG campaign.

CAMPAIGN EVENTS (chronological):
{events}

PROTAGONIST: {protagonist}
ACTIVE VOWS: {vows}
KEY RELATIONSHIPS: {relationships}

Write a {length} summary that captures:
1. The protagonist's journey
2. Major turning points
3. Current situation and stakes
4. Unresolved mysteries

Write in third person, past tense for completed events, present tense for current situation.

OUTPUT ONLY THE SUMMARY TEXT:'''

    CLIFFHANGER_PROMPT = '''Generate a dramatic cliffhanger ending line for an RPG session.

FINAL SCENE: {scene}
UNRESOLVED TENSION: {tension}
PROTAGONIST: {protagonist}

Write ONE dramatic sentence that ends the session on a note of tension/anticipation.
Examples:
- "And in the shadows behind you, something moves."
- "The transmission crackles to life: 'We know where you are.'"
- "As the door seals shut, you realize you're not alone."

OUTPUT ONLY THE CLIFFHANGER LINE:'''

    def __init__(self, llm_provider=None):
        self._provider = llm_provider
        self._session_history: List[SessionSummary] = []
        self._current_session: Optional[SessionSummary] = None

    def _get_provider(self):
        """Lazy-load LLM provider."""
        if self._provider is None:
            try:
                from src.llm_provider import get_provider
                self._provider = get_provider()
            except Exception:
                pass
        return self._provider

    def start_session(self, session_number: int = None):
        """Start tracking a new session."""
        if session_number is None:
            session_number = len(self._session_history) + 1

        self._current_session = SessionSummary(session_number=session_number)

    def record_event(
        self,
        description: str,
        importance: int = 5,
        characters: List[str] = None,
        location: str = "",
        is_cliffhanger: bool = False,
        emotional_tone: str = ""
    ):
        """Record a significant event in the current session."""
        if not self._current_session:
            self.start_session()

        event = SessionEvent(
            description=description,
            importance=importance,
            characters_involved=characters or [],
            location=location,
            is_cliffhanger=is_cliffhanger,
            emotional_tone=emotional_tone,
        )

        self._current_session.events.append(event)

        if is_cliffhanger:
            self._current_session.cliffhanger = description

    def record_decision(self, decision: str):
        """Record a major player decision."""
        if not self._current_session:
            self.start_session()
        self._current_session.major_decisions.append(decision)

    def record_npc_met(self, npc_name: str):
        """Record an NPC encounter."""
        if not self._current_session:
            self.start_session()
        if npc_name not in self._current_session.npcs_met:
            self._current_session.npcs_met.append(npc_name)

    def record_location_visited(self, location: str):
        """Record a location visit."""
        if not self._current_session:
            self.start_session()
        if location not in self._current_session.locations_visited:
            self._current_session.locations_visited.append(location)

    def end_session(self, overall_tone: str = ""):
        """End the current session and archive it."""
        if self._current_session:
            self._current_session.overall_tone = overall_tone

            # Generate one-line summary
            if self._current_session.events:
                top_events = sorted(
                    self._current_session.events,
                    key=lambda e: e.importance,
                    reverse=True
                )[:2]
                self._current_session.one_line_summary = " ".join(
                    e.description for e in top_events
                )

            self._session_history.append(self._current_session)
            self._current_session = None

    def generate_recap(
        self,
        style: RecapStyle = RecapStyle.DRAMATIC,
        length: str = "medium",
        session_index: int = -1
    ) -> str:
        """
        Generate a "Previously on..." recap.

        Args:
            style: Narration style
            length: "short" (2-3 sentences), "medium" (paragraph), "long" (multiple paragraphs)
            session_index: Which session to recap (-1 for most recent)

        Returns:
            Recap text
        """
        if not self._session_history:
            return "No previous sessions to recap."

        session = self._session_history[session_index]

        # Sort events by importance
        sorted_events = sorted(
            session.events,
            key=lambda e: e.importance,
            reverse=True
        )

        # Format events for prompt
        event_text = "\n".join([
            f"- {e.description} (importance: {e.importance}/10)"
            for e in sorted_events[:6]
        ])

        decisions_text = "\n".join([
            f"- {d}" for d in session.major_decisions[:4]
        ]) or "- No major decisions recorded"

        characters_text = ", ".join(session.npcs_met[:5]) or "None recorded"
        locations_text = ", ".join(session.locations_visited[:4]) or "Unknown"

        cliffhanger_section = ""
        if session.cliffhanger:
            cliffhanger_section = f"CLIFFHANGER FROM LAST SESSION:\n{session.cliffhanger}\n(EMPHASIZE THIS!)"

        length_guide = {
            "short": "2-3 sentence",
            "medium": "one paragraph (4-6 sentences)",
            "long": "2-3 paragraph",
        }

        prompt = self.RECAP_PROMPT.format(
            events=event_text,
            decisions=decisions_text,
            characters=characters_text,
            locations=locations_text,
            cliffhanger_section=cliffhanger_section,
            style=style.value,
            length=length_guide.get(length, "one paragraph"),
        )

        # Try LLM generation
        provider = self._get_provider()
        if provider and provider.is_available():
            try:
                recap = provider.chat(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=400,
                )
                if recap and not recap.startswith("["):
                    return recap
            except Exception:
                pass

        # Fallback: simple recap
        return self._generate_fallback_recap(session)

    def _generate_fallback_recap(self, session: SessionSummary) -> str:
        """Generate a simple recap without LLM."""
        parts = ["*Previously...*\n"]

        # Top 3 events
        sorted_events = sorted(
            session.events,
            key=lambda e: e.importance,
            reverse=True
        )[:3]

        for event in sorted_events:
            parts.append(f"• {event.description}")

        if session.cliffhanger:
            parts.append(f"\n*{session.cliffhanger}*")

        return "\n".join(parts)

    def generate_story_so_far(
        self,
        protagonist_name: str = "the protagonist",
        active_vows: List[str] = None,
        key_relationships: Dict[str, str] = None,
        length: str = "medium"
    ) -> str:
        """
        Generate a "story so far" summary of the entire campaign.

        Args:
            protagonist_name: Name of the player character
            active_vows: List of active vow names
            key_relationships: Dict of NPC -> relationship
            length: "short", "medium", or "long"

        Returns:
            Campaign summary text
        """
        if not self._session_history:
            return "The story has not yet begun..."

        # Gather all significant events
        all_events = []
        for session in self._session_history:
            for event in session.events:
                if event.importance >= 6:  # Only high-importance events
                    all_events.append(f"Session {session.session_number}: {event.description}")

        events_text = "\n".join(all_events[-10:])  # Last 10 significant events

        vows_text = ", ".join(active_vows) if active_vows else "None active"

        relationships_text = ""
        if key_relationships:
            relationships_text = "\n".join([
                f"- {npc}: {rel}" for npc, rel in list(key_relationships.items())[:5]
            ])
        else:
            relationships_text = "None established"

        length_guide = {
            "short": "2-3 sentence",
            "medium": "one paragraph",
            "long": "2-3 paragraph",
        }

        prompt = self.SUMMARY_PROMPT.format(
            events=events_text,
            protagonist=protagonist_name,
            vows=vows_text,
            relationships=relationships_text,
            length=length_guide.get(length, "one paragraph"),
        )

        # Try LLM generation
        provider = self._get_provider()
        if provider and provider.is_available():
            try:
                summary = provider.chat(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=300,
                )
                if summary and not summary.startswith("["):
                    return summary
            except Exception:
                pass

        # Fallback
        return self._generate_fallback_summary(protagonist_name)

    def _generate_fallback_summary(self, protagonist_name: str) -> str:
        """Generate a simple summary without LLM."""
        num_sessions = len(self._session_history)

        parts = [
            f"Over {num_sessions} sessions, {protagonist_name} has faced numerous challenges.",
        ]

        # Add most recent session's one-liner
        if self._session_history:
            last = self._session_history[-1]
            if last.one_line_summary:
                parts.append(f"Most recently: {last.one_line_summary}")

        return " ".join(parts)

    def generate_cliffhanger(
        self,
        final_scene: str,
        unresolved_tension: str,
        protagonist_name: str = "you"
    ) -> str:
        """
        Generate a dramatic cliffhanger line to end a session.

        Args:
            final_scene: Description of the current scene
            unresolved_tension: What's at stake/unresolved
            protagonist_name: Name of the protagonist

        Returns:
            Cliffhanger text
        """
        prompt = self.CLIFFHANGER_PROMPT.format(
            scene=final_scene,
            tension=unresolved_tension,
            protagonist=protagonist_name,
        )

        provider = self._get_provider()
        if provider and provider.is_available():
            try:
                cliffhanger = provider.chat(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9,
                    max_tokens=60,
                )
                if cliffhanger and not cliffhanger.startswith("["):
                    return cliffhanger.strip()
            except Exception:
                pass

        # Fallback cliffhangers
        fallbacks = [
            "And then, everything changed.",
            "What happens next... is up to you.",
            "To be continued...",
            "The silence that follows is deafening.",
        ]
        return random.choice(fallbacks)

    def get_recap_for_session_start(
        self,
        protagonist_name: str = "you",
        style: RecapStyle = RecapStyle.DRAMATIC
    ) -> str:
        """
        Get a full recap package for starting a new session.

        Returns formatted text including recap and any relevant context.
        """
        if not self._session_history:
            return f"Welcome, {protagonist_name}. Your story begins now..."

        parts = [
            "═" * 40,
            "**PREVIOUSLY...**",
            "═" * 40,
            "",
            self.generate_recap(style=style, length="medium"),
            "",
            "═" * 40,
        ]

        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize engine state."""
        return {
            "session_history": [s.to_dict() for s in self._session_history],
            "current_session": self._current_session.to_dict() if self._current_session else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionRecapEngine":
        """Deserialize engine state."""
        engine = cls()
        engine._session_history = [
            SessionSummary.from_dict(s)
            for s in data.get("session_history", [])
        ]
        if data.get("current_session"):
            engine._current_session = SessionSummary.from_dict(data["current_session"])
        return engine


# =============================================================================
# AUTO-EXTRACTION FROM NARRATIVE
# =============================================================================

def extract_events_from_narrative(
    narrative: str,
    scene_number: int = 0
) -> List[SessionEvent]:
    """
    Extract significant events from narrative text.

    This is a helper for automatically populating session events.
    """
    import re

    events = []

    # High importance patterns
    high_patterns = [
        (r"killed|slain|died|fell", "death", 9),
        (r"betrayed|deceived", "betrayal", 8),
        (r"discovered|revealed|uncovered", "discovery", 7),
        (r"escaped|fled|rescued", "escape", 7),
        (r"promised|swore|vowed", "promise", 6),
    ]

    # Medium importance patterns
    medium_patterns = [
        (r"attacked|fought|battle", "combat", 5),
        (r"met|encountered|introduced", "encounter", 4),
        (r"arrived|reached|entered", "arrival", 4),
    ]

    narrative_lower = narrative.lower()

    for pattern, event_type, importance in high_patterns + medium_patterns:
        if re.search(pattern, narrative_lower):
            # Extract surrounding context
            match = re.search(pattern, narrative_lower)
            if match:
                start = max(0, match.start() - 50)
                end = min(len(narrative), match.end() + 100)
                context = narrative[start:end].strip()

                events.append(SessionEvent(
                    description=f"{event_type.title()}: {context[:100]}...",
                    importance=importance,
                    emotional_tone=event_type,
                ))

    return events


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SESSION RECAP ENGINE TEST")
    print("=" * 60)

    engine = SessionRecapEngine()

    # Simulate a session
    engine.start_session(session_number=1)

    engine.record_event(
        "Discovered the captain's body in the cargo hold",
        importance=9,
        characters=["Captain Vex"],
        location="Cargo Hold",
        emotional_tone="tense"
    )

    engine.record_event(
        "Interrogated the crew, uncovering hidden tensions",
        importance=7,
        characters=["Engineer Tanaka", "Pilot Reyes"],
        location="Mess Hall"
    )

    engine.record_event(
        "Found encrypted logs revealing the ship's true mission",
        importance=8,
        location="Bridge",
        emotional_tone="mysterious"
    )

    engine.record_event(
        "Someone sabotaged the engines - we're adrift",
        importance=9,
        is_cliffhanger=True,
        emotional_tone="urgent"
    )

    engine.record_decision("Chose to keep the discovery secret from the crew")
    engine.record_npc_met("Engineer Tanaka")
    engine.record_npc_met("Pilot Reyes")
    engine.record_location_visited("Cargo Hold")
    engine.record_location_visited("Mess Hall")

    engine.end_session(overall_tone="mystery")

    # Generate recap
    print("\n--- Generated Recap (Fallback Mode) ---")
    recap = engine.generate_recap(style=RecapStyle.DRAMATIC)
    print(recap)

    # Generate story so far
    print("\n--- Story So Far ---")
    summary = engine.generate_story_so_far(
        protagonist_name="Kira",
        active_vows=["Uncover the truth", "Survive the voyage"],
        key_relationships={"Tanaka": "suspicious", "Reyes": "uneasy ally"}
    )
    print(summary)

    # Generate cliffhanger
    print("\n--- Cliffhanger ---")
    cliffhanger = engine.generate_cliffhanger(
        final_scene="Standing in the darkened engine room",
        unresolved_tension="The saboteur is still among us",
        protagonist_name="Kira"
    )
    print(cliffhanger)

    # Test session start recap
    print("\n--- Session Start Package ---")
    print(engine.get_recap_for_session_start("Kira"))
