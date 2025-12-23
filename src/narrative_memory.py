"""
Narrative Memory System - Callback & Foreshadowing Tracker

Ensures narrative elements introduced early get paid off later,
creating a cohesive and satisfying story experience.

Key Systems:
1. Plant/Payoff Tracker - Setup moments that need resolution
2. Chekhov's Gun - Introduced elements that must matter
3. Recurring Motifs - Themes, symbols, phrases for callbacks
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
import time


@dataclass
class SnapshotEvent:
    """A structured narrative event captured for continuity."""

    event_type: str
    description: str
    scene_index: int
    severity: str = "info"
    related_characters: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "description": self.description,
            "scene_index": self.scene_index,
            "severity": self.severity,
            "related_characters": self.related_characters,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SnapshotEvent":
        return cls(
            event_type=data.get("event_type", "misc"),
            description=data.get("description", ""),
            scene_index=data.get("scene_index", 0),
            severity=data.get("severity", "info"),
            related_characters=data.get("related_characters", []),
            tags=data.get("tags", []),
        )


@dataclass
class NarrativeSnapshot:
    """Compact snapshot of narrative continuity points."""

    scene_index: int
    recent_events: List[SnapshotEvent] = field(default_factory=list)
    active_vows: List[str] = field(default_factory=list)
    unresolved_threads: List[str] = field(default_factory=list)

    def add_recent_event(
        self,
        event_type: str,
        description: str,
        severity: str = "info",
        related_characters: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> SnapshotEvent:
        event = SnapshotEvent(
            event_type=event_type,
            description=description,
            scene_index=self.scene_index,
            severity=severity,
            related_characters=related_characters or [],
            tags=tags or [],
        )
        self.recent_events.append(event)
        return event

    def to_dict(self) -> dict:
        return {
            "scene_index": self.scene_index,
            "recent_events": [e.to_dict() for e in self.recent_events],
            "active_vows": self.active_vows,
            "unresolved_threads": self.unresolved_threads,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeSnapshot":
        snapshot = cls(scene_index=data.get("scene_index", 0))
        snapshot.active_vows = data.get("active_vows", [])
        snapshot.unresolved_threads = data.get("unresolved_threads", [])
        snapshot.recent_events = [
            SnapshotEvent.from_dict(evt) for evt in data.get("recent_events", [])
        ]
        return snapshot


class PlantType(Enum):
    """Types of narrative plants."""
    MYSTERY = "mystery"  # Unanswered question
    PROMISE = "promise"  # Character commitment
    THREAT = "threat"  # Danger introduced
    OBJECT = "object"  # Significant item
    RELATIONSHIP = "relationship"  # Connection established
    SKILL = "skill"  # Ability mentioned
    SECRET = "secret"  # Hidden information


class PayoffStatus(Enum):
    """Status of a plant's payoff."""
    PENDING = "pending"
    PARTIAL = "partial"  # Partially addressed
    RESOLVED = "resolved"
    ABANDONED = "abandoned"  # Intentionally left unresolved


@dataclass
class NarrativePlant:
    """A setup moment that needs payoff."""
    plant_id: str
    plant_type: PlantType
    description: str
    scene_introduced: int
    importance: float  # 0-1, how critical is the payoff
    
    # Payoff tracking
    payoff_status: PayoffStatus = PayoffStatus.PENDING
    payoff_scene: Optional[int] = None
    payoff_description: str = ""
    
    # Context
    involved_characters: List[str] = field(default_factory=list)
    related_themes: List[str] = field(default_factory=list)
    
    def scenes_since_plant(self, current_scene: int) -> int:
        """How many scenes since this was planted."""
        return current_scene - self.scene_introduced
    
    def needs_payoff_soon(self, current_scene: int) -> bool:
        """Check if this plant is overdue for payoff."""
        scenes_elapsed = self.scenes_since_plant(current_scene)
        
        # High importance items need faster payoff
        if self.importance > 0.8 and scenes_elapsed > 5:
            return True
        if self.importance > 0.5 and scenes_elapsed > 10:
            return True
        if scenes_elapsed > 15:
            return True
        
        return False
    
    def to_dict(self) -> dict:
        return {
            "plant_id": self.plant_id,
            "plant_type": self.plant_type.value,
            "description": self.description,
            "scene_introduced": self.scene_introduced,
            "importance": self.importance,
            "payoff_status": self.payoff_status.value,
            "payoff_scene": self.payoff_scene,
            "payoff_description": self.payoff_description,
            "involved_characters": self.involved_characters,
            "related_themes": self.related_themes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NarrativePlant":
        return cls(
            plant_id=data["plant_id"],
            plant_type=PlantType(data["plant_type"]),
            description=data["description"],
            scene_introduced=data["scene_introduced"],
            importance=data["importance"],
            payoff_status=PayoffStatus(data.get("payoff_status", "pending")),
            payoff_scene=data.get("payoff_scene"),
            payoff_description=data.get("payoff_description", ""),
            involved_characters=data.get("involved_characters", []),
            related_themes=data.get("related_themes", []),
        )


@dataclass
class RecurringMotif:
    """A theme, symbol, or phrase that should recur."""
    motif_id: str
    motif_type: str  # "symbol", "phrase", "theme", "imagery"
    description: str
    first_appearance: int
    appearances: List[int] = field(default_factory=list)
    
    # Guidance
    suggested_frequency: int = 3  # Appear every N scenes
    variations: List[str] = field(default_factory=list)
    
    def scenes_since_last(self, current_scene: int) -> int:
        """Scenes since last appearance."""
        if not self.appearances:
            return current_scene - self.first_appearance
        return current_scene - max(self.appearances)
    
    def should_appear_soon(self, current_scene: int) -> bool:
        """Check if motif should recur."""
        return self.scenes_since_last(current_scene) >= self.suggested_frequency
    
    def to_dict(self) -> dict:
        return {
            "motif_id": self.motif_id,
            "motif_type": self.motif_type,
            "description": self.description,
            "first_appearance": self.first_appearance,
            "appearances": self.appearances,
            "suggested_frequency": self.suggested_frequency,
            "variations": self.variations,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RecurringMotif":
        return cls(
            motif_id=data["motif_id"],
            motif_type=data["motif_type"],
            description=data["description"],
            first_appearance=data["first_appearance"],
            appearances=data.get("appearances", []),
            suggested_frequency=data.get("suggested_frequency", 3),
            variations=data.get("variations", []),
        )


@dataclass
class NarrativeMemory:
    """Master tracker for all narrative callbacks and foreshadowing."""
    
    plants: Dict[str, NarrativePlant] = field(default_factory=dict)
    motifs: Dict[str, RecurringMotif] = field(default_factory=dict)
    current_scene: int = 0
    
    _plant_counter: int = 0
    _motif_counter: int = 0
    
    def plant_element(
        self,
        plant_type: PlantType,
        description: str,
        importance: float = 0.5,
        involved_characters: List[str] = None,
        related_themes: List[str] = None,
    ) -> str:
        """Plant a narrative element that needs payoff."""
        self._plant_counter += 1
        plant_id = f"{plant_type.value}_{self._plant_counter:03d}"
        
        plant = NarrativePlant(
            plant_id=plant_id,
            plant_type=plant_type,
            description=description,
            scene_introduced=self.current_scene,
            importance=importance,
            involved_characters=involved_characters or [],
            related_themes=related_themes or [],
        )
        
        self.plants[plant_id] = plant
        return plant_id
    
    def resolve_plant(self, plant_id: str, payoff_description: str):
        """Mark a plant as resolved."""
        if plant_id in self.plants:
            self.plants[plant_id].payoff_status = PayoffStatus.RESOLVED
            self.plants[plant_id].payoff_scene = self.current_scene
            self.plants[plant_id].payoff_description = payoff_description
    
    def add_motif(
        self,
        motif_type: str,
        description: str,
        suggested_frequency: int = 3,
        variations: List[str] = None,
    ) -> str:
        """Add a recurring motif."""
        self._motif_counter += 1
        motif_id = f"motif_{self._motif_counter:03d}"
        
        motif = RecurringMotif(
            motif_id=motif_id,
            motif_type=motif_type,
            description=description,
            first_appearance=self.current_scene,
            suggested_frequency=suggested_frequency,
            variations=variations or [],
        )
        
        self.motifs[motif_id] = motif
        return motif_id
    
    def mark_motif_appearance(self, motif_id: str):
        """Record that a motif appeared in current scene."""
        if motif_id in self.motifs:
            self.motifs[motif_id].appearances.append(self.current_scene)
    
    def get_pending_payoffs(self) -> List[NarrativePlant]:
        """Get plants that need payoff soon."""
        return [
            p for p in self.plants.values()
            if p.payoff_status == PayoffStatus.PENDING and p.needs_payoff_soon(self.current_scene)
        ]
    
    def get_motifs_due(self) -> List[RecurringMotif]:
        """Get motifs that should appear soon."""
        return [
            m for m in self.motifs.values()
            if m.should_appear_soon(self.current_scene)
        ]
    
    def get_narrator_guidance(self) -> str:
        """Generate guidance for narrator about callbacks."""
        sections = []
        
        # Pending payoffs
        pending = self.get_pending_payoffs()
        if pending:
            sections.append("<narrative_callbacks>")
            sections.append("UNRESOLVED PLANTS (need payoff):")
            for plant in pending[:3]:  # Top 3
                scenes_ago = plant.scenes_since_plant(self.current_scene)
                sections.append(f"  - [{plant.plant_type.value.upper()}] {plant.description}")
                sections.append(f"    Planted {scenes_ago} scenes ago | Importance: {plant.importance:.1f}")
                if plant.involved_characters:
                    sections.append(f"    Characters: {', '.join(plant.involved_characters)}")
            sections.append("</narrative_callbacks>")
        
        # Motifs due
        motifs_due = self.get_motifs_due()
        if motifs_due:
            sections.append("\n<recurring_motifs>")
            sections.append("MOTIFS TO WEAVE IN:")
            for motif in motifs_due[:2]:  # Top 2
                sections.append(f"  - [{motif.motif_type}] {motif.description}")
                if motif.variations:
                    sections.append(f"    Variations: {', '.join(motif.variations[:3])}")
            sections.append("</recurring_motifs>")
        
        # Chekhov's Gun reminder
        all_pending = [p for p in self.plants.values() if p.payoff_status == PayoffStatus.PENDING]
        if len(all_pending) > 5:
            sections.append("\n<chekovs_gun>")
            sections.append(f"WARNING: {len(all_pending)} unresolved plants.")
            sections.append("Consider resolving some before introducing new elements.")
            sections.append("</chekovs_gun>")
        
        return "\n".join(sections) if sections else ""
    
    def advance_scene(self):
        """Move to next scene."""
        self.current_scene += 1
    
    def to_dict(self) -> dict:
        return {
            "plants": {pid: p.to_dict() for pid, p in self.plants.items()},
            "motifs": {mid: m.to_dict() for mid, m in self.motifs.items()},
            "current_scene": self.current_scene,
            "_plant_counter": self._plant_counter,
            "_motif_counter": self._motif_counter,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeMemory":
        memory = cls()
        memory.current_scene = data.get("current_scene", 0)
        memory._plant_counter = data.get("_plant_counter", 0)
        memory._motif_counter = data.get("_motif_counter", 0)
        
        for pid, pdata in data.get("plants", {}).items():
            memory.plants[pid] = NarrativePlant.from_dict(pdata)
        
        for mid, mdata in data.get("motifs", {}).items():
            memory.motifs[mid] = RecurringMotif.from_dict(mdata)
        
        return memory


# =============================================================================
# Helper Functions
# =============================================================================

def auto_detect_plants(narrative_text: str, current_scene: int) -> List[tuple]:
    """
    Automatically detect potential plants from narrative text.
    Returns list of (plant_type, description, importance) tuples.
    """
    plants = []
    text_lower = narrative_text.lower()
    
    # Mystery detection
    if "?" in narrative_text or any(word in text_lower for word in ["why", "how", "what if", "where"]):
        # Extract question or mystery
        sentences = narrative_text.split(".")
        for sent in sentences:
            if "?" in sent or any(word in sent.lower() for word in ["mystery", "unknown", "strange"]):
                plants.append((PlantType.MYSTERY, sent.strip()[:100], 0.6))
    
    # Promise detection
    if any(word in text_lower for word in ["promise", "swear", "vow", "will", "must"]):
        plants.append((PlantType.PROMISE, "Character commitment detected", 0.7))
    
    # Threat detection
    if any(word in text_lower for word in ["danger", "threat", "warning", "coming", "hunt"]):
        plants.append((PlantType.THREAT, "Threat introduced", 0.8))
    
    # Object detection (mentioned items)
    if any(word in text_lower for word in ["found", "discovered", "picked up", "took", "carried"]):
        plants.append((PlantType.OBJECT, "Significant item mentioned", 0.5))
    
    return plants
