"""
Camp Journal System.

Logs notable camp moments and manages visual camp state changes
based on arc progression and morale.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CampJournalEntry:
    """A logged moment in camp history."""
    timestamp: datetime
    event_description: str
    characters_involved: list[str] = field(default_factory=list)
    emotional_tone: str = ""  # "hopeful", "tense", "celebratory", etc.
    morale_impact: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_description": self.event_description,
            "characters_involved": self.characters_involved,
            "emotional_tone": self.emotional_tone,
            "morale_impact": self.morale_impact,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CampJournalEntry":
        return cls(
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            event_description=data.get("event_description", ""),
            characters_involved=data.get("characters_involved", []),
            emotional_tone=data.get("emotional_tone", ""),
            morale_impact=data.get("morale_impact", 0.0),
        )


@dataclass
class PropChange:
    """A visual change to camp props."""
    prop_id: str
    prop_type: str  # "decoration", "tent", "equipment", "memorial"
    description: str
    location: str  # Zone ID
    added: bool = True  # True if added, False if removed
    
    def to_dict(self) -> dict:
        return {
            "prop_id": self.prop_id,
            "prop_type": self.prop_type,
            "description": self.description,
            "location": self.location,
            "added": self.added,
        }


@dataclass
class CampVisualState:
    """Current visual state of the camp."""
    props: list[PropChange] = field(default_factory=list)
    overall_condition: str = "maintained"  # "pristine", "maintained", "worn", "deteriorating"
    decorations_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            "props": [p.to_dict() for p in self.props],
            "overall_condition": self.overall_condition,
            "decorations_count": self.decorations_count,
        }


class CampJournal:
    """Manages camp narrative persistence and visual changes."""
    
    def __init__(self):
        self.entries: list[CampJournalEntry] = []
        self.visual_state = CampVisualState()
        self.max_entries = 100  # Keep last 100 entries
    
    def log_moment(
        self,
        event_description: str,
        characters_involved: Optional[list[str]] = None,
        emotional_tone: str = "",
        morale_impact: float = 0.0
    ) -> CampJournalEntry:
        """Log a notable camp moment."""
        entry = CampJournalEntry(
            timestamp=datetime.now(),
            event_description=event_description,
            characters_involved=characters_involved or [],
            emotional_tone=emotional_tone,
            morale_impact=morale_impact,
        )
        
        self.entries.append(entry)
        
        # Trim old entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        
        return entry
    
    def get_visual_changes(
        self,
        crew_morale: float,
        arc_states: dict[str, "ArcState"]
    ) -> list[PropChange]:
        """
        Generate visual changes based on morale and arc progression.
        Returns new props to add/remove.
        """
        changes = []
        
        # Morale-based changes
        if crew_morale > 0.7:
            # High morale: add decorations
            if self.visual_state.decorations_count < 5:
                changes.append(PropChange(
                    prop_id=f"decoration_{len(self.visual_state.props)}",
                    prop_type="decoration",
                    description="Colorful fabric hung between posts",
                    location="common_area",
                    added=True
                ))
                self.visual_state.decorations_count += 1
            
            self.visual_state.overall_condition = "maintained"
        
        elif crew_morale < 0.3:
            # Low morale: camp deteriorates
            if self.visual_state.decorations_count > 0:
                # Remove decorations
                changes.append(PropChange(
                    prop_id=f"decoration_{self.visual_state.decorations_count - 1}",
                    prop_type="decoration",
                    description="Faded decoration removed",
                    location="common_area",
                    added=False
                ))
                self.visual_state.decorations_count -= 1
            
            self.visual_state.overall_condition = "worn"
        
        # Arc-based changes
        for npc_id, arc_state in arc_states.items():
            # Check for specific arc flags that trigger visual changes
            if "memorial_created" in arc_state.flags:
                # Add memorial
                changes.append(PropChange(
                    prop_id=f"memorial_{npc_id}",
                    prop_type="memorial",
                    description=f"Small memorial for Captain Reyes",
                    location="meditation_spot",
                    added=True
                ))
            
            if "personal_space_improved" in arc_state.flags:
                # Improve NPC's bunk
                changes.append(PropChange(
                    prop_id=f"bunk_upgrade_{npc_id}",
                    prop_type="equipment",
                    description=f"{npc_id.title()}'s space shows signs of care",
                    location="sleeping_quarters",
                    added=True
                ))
        
        # Apply changes to visual state
        for change in changes:
            if change.added:
                self.visual_state.props.append(change)
            else:
                # Remove matching prop
                self.visual_state.props = [
                    p for p in self.visual_state.props
                    if p.prop_id != change.prop_id
                ]
        
        return changes
    
    def get_summary(self, limit: int = 10) -> list[dict]:
        """
        Get recent journal entries as UI-friendly summaries.
        
        Args:
            limit: Number of recent entries to return
        
        Returns:
            List of entry dictionaries
        """
        recent_entries = self.entries[-limit:] if self.entries else []
        return [entry.to_dict() for entry in reversed(recent_entries)]
    
    def get_entries_by_character(self, npc_id: str, limit: int = 5) -> list[CampJournalEntry]:
        """Get recent entries involving a specific character."""
        character_entries = [
            entry for entry in self.entries
            if npc_id in entry.characters_involved
        ]
        return character_entries[-limit:] if character_entries else []
    
    def get_entries_by_tone(self, emotional_tone: str, limit: int = 5) -> list[CampJournalEntry]:
        """Get recent entries with a specific emotional tone."""
        tone_entries = [
            entry for entry in self.entries
            if entry.emotional_tone == emotional_tone
        ]
        return tone_entries[-limit:] if tone_entries else []
    
    def generate_narrative_summary(self, days: int = 7) -> str:
        """
        Generate a narrative summary of recent camp events.
        
        Args:
            days: Number of days to summarize (approximated)
        
        Returns:
            Formatted narrative summary
        """
        # Approximate entries per day (assuming ~10 entries per day)
        entries_to_check = min(days * 10, len(self.entries))
        recent = self.entries[-entries_to_check:] if entries_to_check > 0 else []
        
        if not recent:
            return "The camp has been quiet. No notable events recorded."
        
        lines = [f"=== CAMP JOURNAL: LAST {days} DAYS ===\n"]
        
        # Group by emotional tone
        tones = {}
        for entry in recent:
            tone = entry.emotional_tone or "neutral"
            if tone not in tones:
                tones[tone] = []
            tones[tone].append(entry)
        
        # Summarize by tone
        for tone, entries in tones.items():
            lines.append(f"\n{tone.upper()} MOMENTS ({len(entries)}):")
            for entry in entries[-3:]:  # Last 3 of each tone
                chars = ", ".join(entry.characters_involved) if entry.characters_involved else "the crew"
                lines.append(f"  • {entry.event_description} ({chars})")
        
        # Overall morale trend
        morale_impacts = [e.morale_impact for e in recent if e.morale_impact != 0]
        if morale_impacts:
            avg_impact = sum(morale_impacts) / len(morale_impacts)
            if avg_impact > 0.05:
                lines.append("\n📈 Morale has been improving.")
            elif avg_impact < -0.05:
                lines.append("\n📉 Morale has been declining.")
            else:
                lines.append("\n➡️  Morale has been stable.")
        
        return "\n".join(lines)
    
    def integrate_environmental_discovery(
        self,
        discovery: "EnvironmentalDiscovery"
    ) -> None:
        """
        Integrate an environmental discovery into the journal.
        Links with environmental_storytelling.py
        """
        self.log_moment(
            event_description=f"Discovery: {discovery.description}",
            emotional_tone=discovery.tone.value if hasattr(discovery, 'tone') else "",
            morale_impact=0.02  # Small morale boost from discoveries
        )
    
    def to_dict(self) -> dict:
        """Serialize journal state."""
        return {
            "entries": [entry.to_dict() for entry in self.entries[-50:]],  # Last 50
            "visual_state": self.visual_state.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CampJournal":
        """Deserialize journal state."""
        journal = cls()
        
        for entry_data in data.get("entries", []):
            entry = CampJournalEntry.from_dict(entry_data)
            journal.entries.append(entry)
        
        visual_data = data.get("visual_state", {})
        journal.visual_state = CampVisualState(
            props=[PropChange(**p) for p in visual_data.get("props", [])],
            overall_condition=visual_data.get("overall_condition", "maintained"),
            decorations_count=visual_data.get("decorations_count", 0),
        )
        
        return journal


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_camp_journal() -> CampJournal:
    """Create a new camp journal."""
    return CampJournal()


def log_camp_event(
    journal: CampJournal,
    event_name: str,
    participants: list[str],
    morale_effect: float
) -> None:
    """Helper to log a camp event."""
    journal.log_moment(
        event_description=f"Camp event: {event_name}",
        characters_involved=participants,
        emotional_tone="social",
        morale_impact=morale_effect
    )


def log_arc_progression(
    journal: CampJournal,
    npc_id: str,
    new_step: str
) -> None:
    """Helper to log arc progression."""
    journal.log_moment(
        event_description=f"{npc_id.title()}'s story progresses: {new_step.replace('_', ' ')}",
        characters_involved=[npc_id],
        emotional_tone="narrative",
        morale_impact=0.05
    )
