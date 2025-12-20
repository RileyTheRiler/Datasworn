"""
Smart Event Detection System

Uses LLM to analyze narratives for significant events that should trigger
delayed consequences, reputation changes, and world state updates.

This replaces the simple keyword-matching approach with semantic understanding.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import json
import re


class EventType(Enum):
    """Types of significant narrative events."""
    # Violence & Conflict
    KILL = "kill"
    WOUND = "wound"
    DEFEAT = "defeat"
    SPARE = "spare"
    CAPTURE = "capture"
    RESCUE = "rescue"

    # Social & Relationship
    BETRAY = "betray"
    ALLY = "ally"
    PROMISE = "promise"
    BREAK_PROMISE = "break_promise"
    INSULT = "insult"
    THREAT = "threat" # Added for payoff tracking
    CHALLENGE = "challenge"
    HONOR = "honor"
    ROMANCE = "romance"

    # Discovery & Knowledge
    DISCOVER = "discover"
    LEARN_SECRET = "learn_secret"
    REVEAL_SECRET = "reveal_secret"
    SOLVE_MYSTERY = "solve_mystery"

    # Resources & Items
    ACQUIRE = "acquire"
    LOSE = "lose"
    DESTROY = "destroy"
    STEAL = "steal"
    GIFT = "gift"

    # Location & Territory
    CLAIM = "claim"
    ABANDON = "abandon"
    ENTER_FORBIDDEN = "enter_forbidden"
    DESECRATE = "desecrate"

    # Character Development
    OATH = "oath"
    SACRIFICE = "sacrifice"
    TRANSFORMATION = "transformation"
    REVELATION = "revelation"


@dataclass
class DetectedEvent:
    """A significant event detected in the narrative."""
    event_type: EventType
    description: str
    entities: List[str] = field(default_factory=list)
    location: str = ""
    severity: float = 0.5  # 0-1 scale
    witnesses: List[str] = field(default_factory=list)
    consequences: List[str] = field(default_factory=list)
    priority: int = 5  # 1-10, higher = more important

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "description": self.description,
            "entities": self.entities,
            "location": self.location,
            "severity": self.severity,
            "witnesses": self.witnesses,
            "consequences": self.consequences,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectedEvent":
        return cls(
            event_type=EventType(data.get("event_type", "discover")),
            description=data.get("description", ""),
            entities=data.get("entities", []),
            location=data.get("location", ""),
            severity=data.get("severity", 0.5),
            witnesses=data.get("witnesses", []),
            consequences=data.get("consequences", []),
            priority=data.get("priority", 5),
        )


@dataclass
class ConsequenceTemplate:
    """A template for generating narrative consequences."""
    event_type: EventType
    delay_scenes: int  # How many scenes before this triggers
    beat_template: str  # Template with {entity}, {location} placeholders
    priority: int
    requires_witness: bool = False
    faction_impact: Optional[str] = None
    reputation_change: float = 0.0  # -1 to 1

    def generate_beat(self, event: DetectedEvent) -> str:
        """Generate a specific beat from the template."""
        beat = self.beat_template
        if event.entities:
            beat = beat.replace("{entity}", event.entities[0])
            beat = beat.replace("{entities}", ", ".join(event.entities))
        if event.location:
            beat = beat.replace("{location}", event.location)
        return beat


# Pre-defined consequence templates for each event type
CONSEQUENCE_TEMPLATES: Dict[EventType, List[ConsequenceTemplate]] = {
    EventType.KILL: [
        ConsequenceTemplate(
            EventType.KILL, delay_scenes=3,
            beat_template="Someone seeks vengeance for {entity}'s death",
            priority=7, faction_impact="hostile", reputation_change=-0.2
        ),
        ConsequenceTemplate(
            EventType.KILL, delay_scenes=5,
            beat_template="Rumors of the killing reach {location}",
            priority=5, requires_witness=True
        ),
        ConsequenceTemplate(
            EventType.KILL, delay_scenes=2,
            beat_template="{entity}'s allies discover the truth",
            priority=8
        ),
    ],
    EventType.SPARE: [
        ConsequenceTemplate(
            EventType.SPARE, delay_scenes=4,
            beat_template="{entity} returns with unexpected aid",
            priority=6, reputation_change=0.1
        ),
        ConsequenceTemplate(
            EventType.SPARE, delay_scenes=6,
            beat_template="Word of your mercy spreads",
            priority=4, faction_impact="friendly"
        ),
    ],
    EventType.BETRAY: [
        ConsequenceTemplate(
            EventType.BETRAY, delay_scenes=2,
            beat_template="The betrayal is discovered - {entity} plots revenge",
            priority=9, reputation_change=-0.3
        ),
        ConsequenceTemplate(
            EventType.BETRAY, delay_scenes=5,
            beat_template="Others hear of the betrayal and distrust grows",
            priority=6, faction_impact="hostile"
        ),
    ],
    EventType.ALLY: [
        ConsequenceTemplate(
            EventType.ALLY, delay_scenes=3,
            beat_template="{entity} calls in a favor from the alliance",
            priority=5, faction_impact="friendly"
        ),
        ConsequenceTemplate(
            EventType.ALLY, delay_scenes=4,
            beat_template="The alliance opens new opportunities at {location}",
            priority=4, reputation_change=0.15
        ),
    ],
    EventType.DISCOVER: [
        ConsequenceTemplate(
            EventType.DISCOVER, delay_scenes=4,
            beat_template="Others learn of your discovery and seek it",
            priority=5
        ),
        ConsequenceTemplate(
            EventType.DISCOVER, delay_scenes=3,
            beat_template="The discovery's true significance becomes clear",
            priority=6
        ),
    ],
    EventType.LEARN_SECRET: [
        ConsequenceTemplate(
            EventType.LEARN_SECRET, delay_scenes=4,
            beat_template="The secret's keeper realizes you know",
            priority=7
        ),
        ConsequenceTemplate(
            EventType.LEARN_SECRET, delay_scenes=6,
            beat_template="The secret creates an unexpected opportunity",
            priority=5
        ),
    ],
    EventType.PROMISE: [
        ConsequenceTemplate(
            EventType.PROMISE, delay_scenes=5,
            beat_template="{entity} calls upon you to fulfill your promise",
            priority=6
        ),
    ],
    EventType.BREAK_PROMISE: [
        ConsequenceTemplate(
            EventType.BREAK_PROMISE, delay_scenes=2,
            beat_template="{entity} confronts you about the broken promise",
            priority=8, reputation_change=-0.25
        ),
    ],
    EventType.STEAL: [
        ConsequenceTemplate(
            EventType.STEAL, delay_scenes=3,
            beat_template="The theft is discovered - pursuit begins",
            priority=7, reputation_change=-0.15
        ),
    ],
    EventType.GIFT: [
        ConsequenceTemplate(
            EventType.GIFT, delay_scenes=4,
            beat_template="{entity} reciprocates with unexpected generosity",
            priority=4, reputation_change=0.1
        ),
    ],
    EventType.SACRIFICE: [
        ConsequenceTemplate(
            EventType.SACRIFICE, delay_scenes=3,
            beat_template="Your sacrifice is recognized and honored",
            priority=6, reputation_change=0.2
        ),
        ConsequenceTemplate(
            EventType.SACRIFICE, delay_scenes=5,
            beat_template="The sacrifice's effects ripple outward",
            priority=5
        ),
    ],
    EventType.OATH: [
        ConsequenceTemplate(
            EventType.OATH, delay_scenes=4,
            beat_template="The oath is tested by circumstance",
            priority=7
        ),
    ],
    EventType.REVELATION: [
        ConsequenceTemplate(
            EventType.REVELATION, delay_scenes=2,
            beat_template="The revelation changes how others see you",
            priority=6
        ),
    ],
    EventType.RESCUE: [
        ConsequenceTemplate(
            EventType.RESCUE, delay_scenes=3,
            beat_template="{entity} proves their gratitude in unexpected ways",
            priority=5, reputation_change=0.15
        ),
    ],
    EventType.CAPTURE: [
        ConsequenceTemplate(
            EventType.CAPTURE, delay_scenes=2,
            beat_template="Allies of {entity} organize a rescue attempt",
            priority=7
        ),
    ],
    EventType.DESTROY: [
        ConsequenceTemplate(
            EventType.DESTROY, delay_scenes=4,
            beat_template="The destruction's consequences become apparent",
            priority=6
        ),
    ],
}


class SmartEventDetector:
    """
    LLM-powered event detection system.

    Analyzes narrative text to detect significant events and generate
    appropriate consequences for the game world.
    """

    # Keywords for fast pre-filtering (before LLM analysis)
    QUICK_KEYWORDS = {
        EventType.KILL: ["killed", "slain", "murdered", "death", "dead", "fell", "executed"],
        EventType.WOUND: ["wounded", "injured", "hurt", "bleeding", "struck"],
        EventType.SPARE: ["spared", "mercy", "let go", "released", "forgave"],
        EventType.BETRAY: ["betrayed", "deceived", "lied", "double-crossed", "backstabbed"],
        EventType.ALLY: ["allied", "joined forces", "partnership", "agreement", "pact"],
        EventType.DISCOVER: ["discovered", "found", "uncovered", "revealed", "stumbled upon"],
        EventType.LEARN_SECRET: ["secret", "hidden truth", "confidential", "whispered"],
        EventType.PROMISE: ["promised", "swore", "vowed", "pledged", "committed"],
        EventType.STEAL: ["stole", "theft", "took", "pilfered", "swiped"],
        EventType.SACRIFICE: ["sacrificed", "gave up", "surrendered", "forsook"],
        EventType.RESCUE: ["rescued", "saved", "freed", "liberated"],
        EventType.CAPTURE: ["captured", "imprisoned", "detained", "seized"],
    }

    LLM_PROMPT_TEMPLATE = '''Analyze this narrative for significant events that should have future consequences.

NARRATIVE:
{narrative}

CURRENT CONTEXT:
- Location: {location}
- Active NPCs: {npcs}
- Player Character: {player}

Identify events that would realistically cause future consequences. Focus on:
1. Violence (kills, wounds, defeats, captures)
2. Social changes (betrayals, alliances, promises, insults)
3. Discoveries (secrets learned, mysteries solved)
4. Resource changes (items acquired, lost, stolen)
5. Character moments (oaths, sacrifices, revelations)

For each event, provide:
- type: One of [kill, wound, spare, betray, ally, promise, break_promise, discover, learn_secret, steal, gift, sacrifice, oath, revelation, rescue, capture, destroy]
- description: Brief description of what happened
- entities: Names of people/things involved
- severity: 0.0-1.0 (how impactful)
- witnesses: Who saw this happen
- priority: 1-10 (how important for story)

OUTPUT ONLY VALID JSON ARRAY, NO EXPLANATION:
[{{"type": "...", "description": "...", "entities": [...], "severity": 0.5, "witnesses": [...], "priority": 5}}]

If no significant events, output: []'''

    def __init__(self, use_llm: bool = True, llm_provider=None):
        self.use_llm = use_llm
        self._provider = llm_provider
        self._event_history: List[DetectedEvent] = []

    def _get_provider(self):
        """Lazy-load LLM provider."""
        if self._provider is None:
            try:
                from src.llm_provider import get_provider
                self._provider = get_provider()
            except Exception:
                self._provider = None
        return self._provider

    def detect_events(
        self,
        narrative: str,
        location: str = "",
        active_npcs: List[str] = None,
        player_name: str = "the protagonist"
    ) -> List[DetectedEvent]:
        """
        Detect significant events in the narrative.

        Uses quick keyword filtering first, then LLM for deeper analysis.
        Falls back to keyword-only detection if LLM unavailable.
        """
        active_npcs = active_npcs or []

        # Quick filter: check if narrative might contain events
        potential_events = self._quick_keyword_scan(narrative)

        if not potential_events and not self.use_llm:
            return []

        # Try LLM-based detection for richer analysis
        if self.use_llm:
            llm_events = self._llm_detect(narrative, location, active_npcs, player_name)
            if llm_events:
                self._event_history.extend(llm_events)
                return llm_events

        # Fall back to keyword-based detection
        keyword_events = self._keyword_detect(narrative, location, active_npcs)
        self._event_history.extend(keyword_events)
        return keyword_events

    def _quick_keyword_scan(self, narrative: str) -> List[EventType]:
        """Quick scan for potential event types."""
        narrative_lower = narrative.lower()
        potential = []

        for event_type, keywords in self.QUICK_KEYWORDS.items():
            if any(kw in narrative_lower for kw in keywords):
                potential.append(event_type)

        return potential

    def _llm_detect(
        self,
        narrative: str,
        location: str,
        active_npcs: List[str],
        player_name: str
    ) -> List[DetectedEvent]:
        """Use LLM to detect events with semantic understanding."""
        provider = self._get_provider()
        if not provider or not provider.is_available():
            return []

        prompt = self.LLM_PROMPT_TEMPLATE.format(
            narrative=narrative[:2000],  # Limit length
            location=location or "unknown",
            npcs=", ".join(active_npcs[:5]) if active_npcs else "none present",
            player=player_name,
        )

        try:
            response = provider.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temp for more consistent output
                max_tokens=512,
            )

            # Parse JSON response
            events = self._parse_llm_response(response, location)
            return events

        except Exception as e:
            import logging
            logging.getLogger("smart_events").warning(f"LLM detection failed: {e}")
            return []

    def _parse_llm_response(self, response: str, location: str) -> List[DetectedEvent]:
        """Parse LLM JSON response into DetectedEvent objects."""
        events = []

        # Find JSON array in response
        json_start = response.find("[")
        json_end = response.rfind("]") + 1

        if json_start < 0 or json_end <= json_start:
            return []

        try:
            raw_events = json.loads(response[json_start:json_end])

            for raw in raw_events:
                try:
                    event_type = EventType(raw.get("type", "discover"))
                except ValueError:
                    continue

                events.append(DetectedEvent(
                    event_type=event_type,
                    description=raw.get("description", ""),
                    entities=raw.get("entities", []),
                    location=location,
                    severity=float(raw.get("severity", 0.5)),
                    witnesses=raw.get("witnesses", []),
                    priority=int(raw.get("priority", 5)),
                ))
        except json.JSONDecodeError:
            pass

        return events

    def _keyword_detect(
        self,
        narrative: str,
        location: str,
        active_npcs: List[str]
    ) -> List[DetectedEvent]:
        """Fallback keyword-based event detection."""
        events = []
        narrative_lower = narrative.lower()

        # Extract names from narrative for entity attribution
        names = self._extract_names(narrative)

        for event_type, keywords in self.QUICK_KEYWORDS.items():
            for keyword in keywords:
                if keyword in narrative_lower:
                    # Find context around keyword
                    idx = narrative_lower.find(keyword)
                    context = narrative[max(0, idx-50):idx+100]

                    # Try to find associated entity
                    entities = []
                    for name in names:
                        if name.lower() in context.lower():
                            entities.append(name)

                    events.append(DetectedEvent(
                        event_type=event_type,
                        description=f"{keyword.title()} detected in narrative",
                        entities=entities[:2] if entities else active_npcs[:1],
                        location=location,
                        severity=0.5,
                        witnesses=active_npcs[:2],
                        priority=self._get_default_priority(event_type),
                    ))
                    break  # One event per type

        return events

    def _extract_names(self, text: str) -> List[str]:
        """Extract potential character names from text."""
        # Pattern for capitalized words that look like names
        name_pattern = r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b'
        matches = re.findall(name_pattern, text)

        # Filter common non-names
        excluded = {"The", "This", "That", "Then", "There", "They", "What", "When",
                   "Where", "Which", "While", "After", "Before", "During", "Into"}

        return [m for m in matches if m not in excluded][:10]

    def _get_default_priority(self, event_type: EventType) -> int:
        """Get default priority for an event type."""
        high_priority = {EventType.KILL, EventType.BETRAY, EventType.CAPTURE}
        medium_priority = {EventType.SPARE, EventType.ALLY, EventType.DISCOVER, EventType.RESCUE}

        if event_type in high_priority:
            return 7
        elif event_type in medium_priority:
            return 5
        return 4

    def generate_consequences(
        self,
        event: DetectedEvent,
        max_consequences: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Generate delayed beat consequences for an event.

        Returns list of consequence dicts with:
        - beat: The narrative beat text
        - trigger_after_scenes: When to trigger
        - priority: Importance
        - faction_impact: Optional faction reputation change
        """
        templates = CONSEQUENCE_TEMPLATES.get(event.event_type, [])

        if not templates:
            # Generic fallback
            return [{
                "beat": f"The events involving {', '.join(event.entities) or 'unknown parties'} have consequences",
                "trigger_after_scenes": 4,
                "priority": event.priority,
            }]

        consequences = []
        for template in templates[:max_consequences]:
            # Skip witness-required templates if no witnesses
            if template.requires_witness and not event.witnesses:
                continue

            # Scale delay by severity (more severe = faster consequences)
            delay = max(1, int(template.delay_scenes * (1.5 - event.severity)))

            consequences.append({
                "beat": template.generate_beat(event),
                "trigger_after_scenes": delay,
                "priority": max(template.priority, event.priority),
                "faction_impact": template.faction_impact,
                "reputation_change": template.reputation_change,
                "source_event": event.event_type.value,
            })

        return consequences

    def get_all_consequences(
        self,
        events: List[DetectedEvent],
        max_total: int = 4
    ) -> List[Dict[str, Any]]:
        """Generate consequences for multiple events, limited to avoid overload."""
        all_consequences = []

        # Sort events by priority (highest first)
        sorted_events = sorted(events, key=lambda e: e.priority, reverse=True)

        for event in sorted_events:
            if len(all_consequences) >= max_total:
                break

            event_consequences = self.generate_consequences(
                event,
                max_consequences=max(1, max_total - len(all_consequences))
            )
            all_consequences.extend(event_consequences)

        # Sort by priority and limit
        all_consequences.sort(key=lambda c: c.get("priority", 5), reverse=True)
        return all_consequences[:max_total]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize detector state."""
        return {
            "use_llm": self.use_llm,
            "event_history": [e.to_dict() for e in self._event_history[-20:]],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SmartEventDetector":
        """Deserialize detector state."""
        detector = cls(use_llm=data.get("use_llm", True))
        detector._event_history = [
            DetectedEvent.from_dict(e)
            for e in data.get("event_history", [])
        ]
        return detector


# =============================================================================
# INTEGRATION HELPER
# =============================================================================

def detect_and_generate_consequences(
    narrative: str,
    location: str = "",
    active_npcs: List[str] = None,
    player_name: str = "the protagonist",
    detector: SmartEventDetector = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function for detecting events and generating consequences.

    Use this in the world_state_manager_node to replace keyword matching.
    """
    if detector is None:
        detector = SmartEventDetector(use_llm=True)

    events = detector.detect_events(
        narrative=narrative,
        location=location,
        active_npcs=active_npcs or [],
        player_name=player_name,
    )

    if not events:
        return []

    return detector.get_all_consequences(events, max_total=3)


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SMART EVENT DETECTION TEST")
    print("=" * 60)

    # Test narrative
    test_narrative = '''
    Kira's blade found its mark. The raider captain crumpled to the deck,
    his final breath a whispered curse. The crew watched in silence—even
    Vasquez, normally quick with a quip, had nothing to say.

    "It had to be done," Kira said, wiping her blade clean. But the look
    in Engineer Tanaka's eyes suggested not everyone agreed.

    In the captain's quarters, they discovered encrypted logs revealing
    the coordinates of a hidden fuel cache. The information could be worth
    a fortune to the right buyer.
    '''

    detector = SmartEventDetector(use_llm=False)  # Test without LLM

    print("\n--- Keyword Detection Test ---")
    events = detector.detect_events(
        test_narrative,
        location="Abandoned Station",
        active_npcs=["Kira", "Vasquez", "Tanaka"],
        player_name="Kira"
    )

    for event in events:
        print(f"\nEvent: {event.event_type.value}")
        print(f"  Description: {event.description}")
        print(f"  Entities: {event.entities}")
        print(f"  Priority: {event.priority}")

        consequences = detector.generate_consequences(event)
        print(f"  Consequences:")
        for c in consequences:
            print(f"    - {c['beat']} (in {c['trigger_after_scenes']} scenes)")
