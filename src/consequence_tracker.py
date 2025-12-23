"""
Consequence Tracker - Track and remind players of unresolved complications.
Helps ensure weak hits and misses have lasting narrative impact.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from datetime import datetime
import uuid

from src.logging_config import get_logger
from src.narrative_memory import NarrativeSnapshot

logger = get_logger("consequences")


class ConsequenceType(str, Enum):
    """Categories of consequences from play."""
    INJURY = "injury"           # Physical harm, reduced health
    DEBT = "debt"               # Owed favor, obligation
    ENEMY = "enemy"             # Made an enemy, vendetta
    COMPLICATION = "complication"  # Generic obstacle
    CLOCK = "clock"             # Ticking time pressure
    LOSS = "loss"               # Lost resource, relationship
    SUSPICION = "suspicion"     # Drawn attention, being watched
    DAMAGE = "damage"           # Equipment/ship damage
    TRAUMA = "trauma"           # Psychological impact


class ConsequenceSeverity(str, Enum):
    """How urgent/severe the consequence is."""
    MINOR = "minor"       # Background flavor, can be ignored
    MODERATE = "moderate" # Should address eventually
    MAJOR = "major"       # Actively causing problems
    CRITICAL = "critical" # Must address soon or escalates


@dataclass
class Consequence:
    """A tracked consequence from gameplay."""
    id: str
    type: ConsequenceType
    severity: ConsequenceSeverity
    description: str
    source: str  # What caused this (move name, oracle result, etc.)
    created_turn: int
    resolved: bool = False
    resolution: str = ""
    escalation_count: int = 0
    related_npc: Optional[str] = None
    related_location: Optional[str] = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "description": self.description,
            "source": self.source,
            "created_turn": self.created_turn,
            "resolved": self.resolved,
            "resolution": self.resolution,
            "escalation_count": self.escalation_count,
            "related_npc": self.related_npc,
            "related_location": self.related_location,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Consequence":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=ConsequenceType(data.get("type", "complication")),
            severity=ConsequenceSeverity(data.get("severity", "moderate")),
            description=data.get("description", ""),
            source=data.get("source", "unknown"),
            created_turn=data.get("created_turn", 0),
            resolved=data.get("resolved", False),
            resolution=data.get("resolution", ""),
            escalation_count=data.get("escalation_count", 0),
            related_npc=data.get("related_npc"),
            related_location=data.get("related_location"),
            tags=data.get("tags", []),
        )


@dataclass
class ConsequenceTracker:
    """Tracks all consequences and provides reminders."""
    consequences: list[Consequence] = field(default_factory=list)
    current_turn: int = 0

    def add_consequence(
        self,
        description: str,
        type: ConsequenceType = ConsequenceType.COMPLICATION,
        severity: ConsequenceSeverity = ConsequenceSeverity.MODERATE,
        source: str = "unknown",
        related_npc: Optional[str] = None,
        related_location: Optional[str] = None,
        tags: Optional[list[str]] = None,
        snapshot: Optional[NarrativeSnapshot] = None,
    ) -> Consequence:
        """Add a new consequence to track."""
        consequence = Consequence(
            id=str(uuid.uuid4())[:8],
            type=type,
            severity=severity,
            description=description,
            source=source,
            created_turn=self.current_turn,
            related_npc=related_npc,
            related_location=related_location,
            tags=tags or [],
        )
        self.consequences.append(consequence)
        logger.debug(f"Added consequence: {description} ({type.value}/{severity.value})")
        if snapshot:
            snapshot.add_recent_event(
                event_type="consequence_added",
                description=description,
                severity=severity.value,
                related_characters=[related_npc] if related_npc else [],
                tags=consequence.tags,
            )
        return consequence

    def resolve_consequence(
        self, consequence_id: str, resolution: str, snapshot: Optional[NarrativeSnapshot] = None
    ) -> bool:
        """Mark a consequence as resolved."""
        for c in self.consequences:
            if c.id == consequence_id:
                c.resolved = True
                c.resolution = resolution
                logger.debug(f"Resolved consequence {consequence_id}: {resolution}")
                if snapshot:
                    snapshot.add_recent_event(
                        event_type="consequence_resolved",
                        description=resolution,
                        severity=c.severity.value,
                        related_characters=[c.related_npc] if c.related_npc else [],
                        tags=c.tags,
                    )
                return True
        return False

    def escalate_consequence(
        self, consequence_id: str, snapshot: Optional[NarrativeSnapshot] = None
    ) -> Optional[Consequence]:
        """Escalate an unresolved consequence (increase severity)."""
        for c in self.consequences:
            if c.id == consequence_id and not c.resolved:
                c.escalation_count += 1

                # Upgrade severity
                severity_order = [
                    ConsequenceSeverity.MINOR,
                    ConsequenceSeverity.MODERATE,
                    ConsequenceSeverity.MAJOR,
                    ConsequenceSeverity.CRITICAL,
                ]
                current_idx = severity_order.index(c.severity)
                if current_idx < len(severity_order) - 1:
                    c.severity = severity_order[current_idx + 1]
                    logger.debug(f"Escalated consequence {consequence_id} to {c.severity.value}")
                if snapshot:
                    snapshot.add_recent_event(
                        event_type="consequence_escalated",
                        description=c.description,
                        severity=c.severity.value,
                        related_characters=[c.related_npc] if c.related_npc else [],
                        tags=c.tags,
                    )

                return c
        return None

    def get_active_consequences(self) -> list[Consequence]:
        """Get all unresolved consequences."""
        return [c for c in self.consequences if not c.resolved]

    def get_consequences_by_severity(self, min_severity: ConsequenceSeverity) -> list[Consequence]:
        """Get active consequences at or above a severity level."""
        severity_order = [
            ConsequenceSeverity.MINOR,
            ConsequenceSeverity.MODERATE,
            ConsequenceSeverity.MAJOR,
            ConsequenceSeverity.CRITICAL,
        ]
        min_idx = severity_order.index(min_severity)

        return [
            c for c in self.get_active_consequences()
            if severity_order.index(c.severity) >= min_idx
        ]

    def get_consequences_for_location(self, location: str) -> list[Consequence]:
        """Get active consequences related to a location."""
        return [
            c for c in self.get_active_consequences()
            if c.related_location and location.lower() in c.related_location.lower()
        ]

    def get_consequences_for_npc(self, npc_name: str) -> list[Consequence]:
        """Get active consequences related to an NPC."""
        return [
            c for c in self.get_active_consequences()
            if c.related_npc and npc_name.lower() in c.related_npc.lower()
        ]

    def get_stale_consequences(self, turns_threshold: int = 5) -> list[Consequence]:
        """Get consequences that have been unresolved for too long."""
        return [
            c for c in self.get_active_consequences()
            if self.current_turn - c.created_turn >= turns_threshold
        ]

    def advance_turn(self, snapshot: Optional[NarrativeSnapshot] = None) -> list[Consequence]:
        """
        Advance the turn counter and check for auto-escalations.

        Returns:
            List of consequences that escalated
        """
        self.current_turn += 1
        escalated = []

        # Escalate stale major/critical consequences
        for c in self.get_active_consequences():
            turns_old = self.current_turn - c.created_turn

            # Critical consequences escalate every 3 turns
            if c.severity == ConsequenceSeverity.CRITICAL and turns_old > 0 and turns_old % 3 == 0:
                self.escalate_consequence(c.id, snapshot=snapshot)
                escalated.append(c)
            # Major consequences escalate every 5 turns
            elif c.severity == ConsequenceSeverity.MAJOR and turns_old > 0 and turns_old % 5 == 0:
                self.escalate_consequence(c.id, snapshot=snapshot)
                escalated.append(c)

        if snapshot and escalated:
            for c in escalated:
                snapshot.add_recent_event(
                    event_type="consequence_progressed",
                    description=c.description,
                    severity=c.severity.value,
                    related_characters=[c.related_npc] if c.related_npc else [],
                    tags=c.tags,
                )

        return escalated

    def to_dict(self) -> dict[str, Any]:
        return {
            "consequences": [c.to_dict() for c in self.consequences],
            "current_turn": self.current_turn,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConsequenceTracker":
        tracker = cls(current_turn=data.get("current_turn", 0))
        for c_data in data.get("consequences", []):
            tracker.consequences.append(Consequence.from_dict(c_data))
        return tracker


def generate_consequence_reminder(tracker: ConsequenceTracker) -> str:
    """
    Generate a narrative reminder about active consequences.

    Args:
        tracker: ConsequenceTracker instance

    Returns:
        Formatted reminder for narrator injection
    """
    active = tracker.get_active_consequences()
    if not active:
        return ""

    # Group by severity
    critical = [c for c in active if c.severity == ConsequenceSeverity.CRITICAL]
    major = [c for c in active if c.severity == ConsequenceSeverity.MAJOR]
    moderate = [c for c in active if c.severity == ConsequenceSeverity.MODERATE]

    lines = ["[ACTIVE CONSEQUENCES - Weave into narrative when relevant]"]

    if critical:
        lines.append("\n⚠ CRITICAL (must address):")
        for c in critical:
            lines.append(f"  • {c.description}")
            if c.escalation_count > 0:
                lines.append(f"    (Escalated {c.escalation_count}x)")

    if major:
        lines.append("\n⚡ MAJOR (causing problems):")
        for c in major[:3]:
            lines.append(f"  • {c.description}")

    if moderate and len(lines) < 10:
        lines.append("\n○ MODERATE (lingering):")
        for c in moderate[:2]:
            lines.append(f"  • {c.description}")

    return "\n".join(lines)


def generate_consequence_from_roll(
    outcome: str,
    move_name: str,
    context: str,
) -> Optional[dict[str, Any]]:
    """
    Suggest a consequence based on roll outcome.

    Args:
        outcome: "strong_hit", "weak_hit", or "miss"
        move_name: Name of the move that was rolled
        context: Narrative context

    Returns:
        Dict with suggested consequence details or None
    """
    if outcome == "strong_hit":
        return None

    if outcome == "weak_hit":
        return {
            "severity": "minor",
            "type": "complication",
            "prompt": f"What complication or cost comes with this partial success on {move_name}?",
            "examples": [
                "You succeed, but draw unwanted attention",
                "It works, but costs precious time or resources",
                "You achieve your goal, but reveal something about yourself",
            ],
        }

    if outcome == "miss":
        return {
            "severity": "moderate",
            "type": "complication",
            "prompt": f"What goes wrong with this failed {move_name}?",
            "examples": [
                "The situation escalates dangerously",
                "You make a new enemy or lose an ally's trust",
                "Something valuable is lost or damaged",
                "You are forced into a difficult choice",
            ],
        }

    return None


def get_consequence_display(tracker: ConsequenceTracker) -> list[dict[str, Any]]:
    """
    Get consequences formatted for UI display.

    Args:
        tracker: ConsequenceTracker instance

    Returns:
        List of consequence dicts with display formatting
    """
    active = tracker.get_active_consequences()

    displays = []
    for c in active:
        age = tracker.current_turn - c.created_turn

        # Determine urgency color
        if c.severity == ConsequenceSeverity.CRITICAL:
            urgency = "critical"
            icon = "🔴"
        elif c.severity == ConsequenceSeverity.MAJOR:
            urgency = "high"
            icon = "🟠"
        elif c.severity == ConsequenceSeverity.MODERATE:
            urgency = "medium"
            icon = "🟡"
        else:
            urgency = "low"
            icon = "⚪"

        displays.append({
            "id": c.id,
            "description": c.description,
            "type": c.type.value,
            "severity": c.severity.value,
            "urgency": urgency,
            "icon": icon,
            "source": c.source,
            "age_turns": age,
            "escalation_count": c.escalation_count,
            "related_npc": c.related_npc,
            "related_location": c.related_location,
        })

    # Sort by severity (critical first)
    severity_order = {"critical": 0, "major": 1, "moderate": 2, "minor": 3}
    displays.sort(key=lambda x: severity_order.get(x["severity"], 4))

    return displays
