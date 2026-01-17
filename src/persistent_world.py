"""
Persistent World Changes System

Tracks permanent changes to the game world that persist across sessions:
- NPC deaths and status changes
- Location destruction or transformation
- Faction control changes
- Territory claims
- World-altering events

Ensures dead NPCs stay dead and destroyed locations stay destroyed.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from enum import Enum
from datetime import datetime
import re

from src.lore import LoreRegistry


class EntityStatus(Enum):
    """Status of world entities."""
    ACTIVE = "active"
    DEAD = "dead"
    DESTROYED = "destroyed"
    TRANSFORMED = "transformed"
    MISSING = "missing"
    CAPTURED = "captured"
    ALLIED = "allied"
    HOSTILE = "hostile"
    NEUTRAL = "neutral"


class ChangeType(Enum):
    """Types of world changes."""
    # Entity changes
    NPC_DEATH = "npc_death"
    NPC_CAPTURED = "npc_captured"
    NPC_FREED = "npc_freed"
    NPC_RELATIONSHIP = "npc_relationship"
    NPC_LOCATION = "npc_location"

    # Location changes
    LOCATION_DESTROYED = "location_destroyed"
    LOCATION_DISCOVERED = "location_discovered"
    LOCATION_CLAIMED = "location_claimed"
    LOCATION_ABANDONED = "location_abandoned"
    LOCATION_TRANSFORMED = "location_transformed"

    # Faction changes
    FACTION_ALLIANCE = "faction_alliance"
    FACTION_WAR = "faction_war"
    FACTION_DESTROYED = "faction_destroyed"
    FACTION_CONTROL = "faction_control"

    # Item changes
    ITEM_ACQUIRED = "item_acquired"
    ITEM_LOST = "item_lost"
    ITEM_DESTROYED = "item_destroyed"
    ITEM_GIVEN = "item_given"

    # World state changes
    SECRET_REVEALED = "secret_revealed"
    VOW_FULFILLED = "vow_fulfilled"
    VOW_FORSAKEN = "vow_forsaken"
    MAJOR_EVENT = "major_event"


@dataclass
class WorldChange:
    """Represents a single permanent change to the world."""
    change_type: ChangeType
    entity_id: str  # NPC name, location ID, faction ID, etc.
    entity_type: str  # "npc", "location", "faction", "item"
    description: str
    old_state: Optional[str] = None
    new_state: Optional[str] = None
    location: Optional[str] = None
    caused_by: Optional[str] = None  # Who/what caused the change
    scene_number: int = 0
    session_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    is_reversible: bool = False
    reversal_condition: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_type": self.change_type.value,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "description": self.description,
            "old_state": self.old_state,
            "new_state": self.new_state,
            "location": self.location,
            "caused_by": self.caused_by,
            "scene_number": self.scene_number,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "is_reversible": self.is_reversible,
            "reversal_condition": self.reversal_condition,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldChange":
        return cls(
            change_type=ChangeType(data["change_type"]),
            entity_id=data["entity_id"],
            entity_type=data["entity_type"],
            description=data["description"],
            old_state=data.get("old_state"),
            new_state=data.get("new_state"),
            location=data.get("location"),
            caused_by=data.get("caused_by"),
            scene_number=data.get("scene_number", 0),
            session_id=data.get("session_id", ""),
            timestamp=data.get("timestamp", ""),
            is_reversible=data.get("is_reversible", False),
            reversal_condition=data.get("reversal_condition"),
        )


@dataclass
class EntityState:
    """Current state of a tracked entity."""
    entity_id: str
    entity_type: str
    status: EntityStatus
    location: Optional[str] = None
    faction: Optional[str] = None
    relationships: Dict[str, str] = field(default_factory=dict)  # entity_id -> relationship
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties
    change_history: List[str] = field(default_factory=list)  # List of change descriptions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "status": self.status.value,
            "location": self.location,
            "faction": self.faction,
            "relationships": self.relationships,
            "properties": self.properties,
            "change_history": self.change_history[-10:],  # Keep last 10
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityState":
        return cls(
            entity_id=data["entity_id"],
            entity_type=data["entity_type"],
            status=EntityStatus(data["status"]),
            location=data.get("location"),
            faction=data.get("faction"),
            relationships=data.get("relationships", {}),
            properties=data.get("properties", {}),
            change_history=data.get("change_history", []),
        )


class PersistentWorldEngine:
    """
    Engine for tracking and enforcing persistent world changes.

    Features:
    - Track NPC deaths permanently
    - Track location destruction/transformation
    - Track faction control changes
    - Generate narrator constraints for dead/destroyed entities
    - Provide world state queries
    """

    def __init__(self):
        self._entities: Dict[str, EntityState] = {}  # entity_id -> EntityState
        self._changes: List[WorldChange] = []
        self._dead_npcs: Set[str] = set()
        self._destroyed_locations: Set[str] = set()
        self._faction_control: Dict[str, str] = {}  # location -> faction
        self._revealed_secrets: Set[str] = set()
        self._current_scene: int = 0
        self._current_session: str = ""
        self._lore_registry: LoreRegistry | None = None

    def attach_lore_registry(self, lore_registry: LoreRegistry) -> None:
        """Attach a lore registry so world changes can unlock codex entries."""

        self._lore_registry = lore_registry

    def set_context(self, scene_number: int, session_id: str = ""):
        """Set current context for change tracking."""
        self._current_scene = scene_number
        self._current_session = session_id

    def record_change(self, change: WorldChange) -> None:
        """Record a world change and update entity states."""
        change.scene_number = self._current_scene
        change.session_id = self._current_session
        self._changes.append(change)

        # Update entity state
        entity = self._get_or_create_entity(
            change.entity_id,
            change.entity_type
        )

        # Apply change to entity
        self._apply_change(entity, change)

        # Update tracking sets
        if change.change_type == ChangeType.NPC_DEATH:
            self._dead_npcs.add(change.entity_id.lower())
        elif change.change_type == ChangeType.LOCATION_DESTROYED:
            self._destroyed_locations.add(change.entity_id.lower())
        elif change.change_type == ChangeType.SECRET_REVEALED:
            self._revealed_secrets.add(change.entity_id)
        elif change.change_type == ChangeType.FACTION_CONTROL:
            if change.location:
                self._faction_control[change.location] = change.entity_id

        if self._lore_registry:
            self._lore_registry.link_world_change(change)

    def _get_or_create_entity(self, entity_id: str, entity_type: str) -> EntityState:
        """Get existing entity or create new one."""
        key = entity_id.lower()
        if key not in self._entities:
            self._entities[key] = EntityState(
                entity_id=entity_id,
                entity_type=entity_type,
                status=EntityStatus.ACTIVE,
            )
        return self._entities[key]

    def _apply_change(self, entity: EntityState, change: WorldChange) -> None:
        """Apply a change to an entity's state."""
        entity.change_history.append(f"[Scene {change.scene_number}] {change.description}")

        if change.change_type == ChangeType.NPC_DEATH:
            entity.status = EntityStatus.DEAD
        elif change.change_type == ChangeType.NPC_CAPTURED:
            entity.status = EntityStatus.CAPTURED
        elif change.change_type == ChangeType.NPC_FREED:
            entity.status = EntityStatus.ACTIVE
        elif change.change_type == ChangeType.LOCATION_DESTROYED:
            entity.status = EntityStatus.DESTROYED
        elif change.change_type == ChangeType.LOCATION_TRANSFORMED:
            entity.status = EntityStatus.TRANSFORMED
            entity.properties["transformed_to"] = change.new_state
        elif change.change_type == ChangeType.NPC_LOCATION:
            entity.location = change.new_state
        elif change.change_type == ChangeType.NPC_RELATIONSHIP:
            if change.caused_by:
                entity.relationships[change.caused_by] = change.new_state or "changed"
        elif change.change_type == ChangeType.FACTION_CONTROL:
            entity.location = change.location

    # =========================================================================
    # CONVENIENCE METHODS FOR COMMON CHANGES
    # =========================================================================

    def record_npc_death(
        self,
        npc_name: str,
        location: str = "",
        caused_by: str = "",
        description: str = ""
    ) -> None:
        """Record an NPC death."""
        self.record_change(WorldChange(
            change_type=ChangeType.NPC_DEATH,
            entity_id=npc_name,
            entity_type="npc",
            description=description or f"{npc_name} was killed",
            old_state="alive",
            new_state="dead",
            location=location,
            caused_by=caused_by,
            is_reversible=False,
        ))

    def record_location_destroyed(
        self,
        location_name: str,
        caused_by: str = "",
        description: str = ""
    ) -> None:
        """Record a location destruction."""
        self.record_change(WorldChange(
            change_type=ChangeType.LOCATION_DESTROYED,
            entity_id=location_name,
            entity_type="location",
            description=description or f"{location_name} was destroyed",
            old_state="intact",
            new_state="destroyed",
            caused_by=caused_by,
            is_reversible=False,
        ))

    def record_faction_control(
        self,
        faction_name: str,
        location: str,
        previous_faction: str = "",
        description: str = ""
    ) -> None:
        """Record a faction taking control of a location."""
        self.record_change(WorldChange(
            change_type=ChangeType.FACTION_CONTROL,
            entity_id=faction_name,
            entity_type="faction",
            description=description or f"{faction_name} took control of {location}",
            old_state=previous_faction,
            new_state=faction_name,
            location=location,
        ))

    def record_secret_revealed(
        self,
        secret_id: str,
        description: str,
        revealed_by: str = ""
    ) -> None:
        """Record a secret being revealed."""
        self.record_change(WorldChange(
            change_type=ChangeType.SECRET_REVEALED,
            entity_id=secret_id,
            entity_type="secret",
            description=description,
            caused_by=revealed_by,
            is_reversible=False,
        ))

    def record_item_change(
        self,
        item_name: str,
        change_type: ChangeType,
        owner: str = "",
        description: str = ""
    ) -> None:
        """Record an item acquisition, loss, or destruction."""
        self.record_change(WorldChange(
            change_type=change_type,
            entity_id=item_name,
            entity_type="item",
            description=description or f"{item_name} was {change_type.value.split('_')[1]}",
            caused_by=owner,
        ))

    # =========================================================================
    # QUERY METHODS
    # =========================================================================

    def is_npc_dead(self, npc_name: str) -> bool:
        """Check if an NPC is dead."""
        return npc_name.lower() in self._dead_npcs

    def is_location_destroyed(self, location_name: str) -> bool:
        """Check if a location is destroyed."""
        return location_name.lower() in self._destroyed_locations

    def is_secret_revealed(self, secret_id: str) -> bool:
        """Check if a secret has been revealed."""
        return secret_id in self._revealed_secrets

    def get_faction_controlling(self, location: str) -> Optional[str]:
        """Get the faction controlling a location."""
        return self._faction_control.get(location)

    def get_entity_state(self, entity_id: str) -> Optional[EntityState]:
        """Get the current state of an entity."""
        return self._entities.get(entity_id.lower())

    def get_dead_npcs(self) -> List[str]:
        """Get list of all dead NPCs."""
        return list(self._dead_npcs)

    def get_destroyed_locations(self) -> List[str]:
        """Get list of all destroyed locations."""
        return list(self._destroyed_locations)

    def get_changes_since(self, scene_number: int) -> List[WorldChange]:
        """Get all changes since a specific scene."""
        return [c for c in self._changes if c.scene_number >= scene_number]

    def get_entity_history(self, entity_id: str) -> List[WorldChange]:
        """Get all changes related to an entity."""
        key = entity_id.lower()
        return [c for c in self._changes if c.entity_id.lower() == key]

    # =========================================================================
    # NARRATOR INTEGRATION
    # =========================================================================

    def get_narrator_constraints(self) -> str:
        """
        Generate narrator constraints based on world state.

        This should be injected into the narrator's system prompt to
        prevent contradictions.
        """
        constraints = []

        # Dead NPCs
        if self._dead_npcs:
            dead_list = ", ".join(sorted(self._dead_npcs))
            constraints.append(
                f"DEAD CHARACTERS (do not bring back or show alive): {dead_list}"
            )

        # Destroyed locations
        if self._destroyed_locations:
            destroyed_list = ", ".join(sorted(self._destroyed_locations))
            constraints.append(
                f"DESTROYED LOCATIONS (do not show intact): {destroyed_list}"
            )

        # Faction control
        if self._faction_control:
            control_list = [f"{loc}: {faction}" for loc, faction in self._faction_control.items()]
            constraints.append(
                f"FACTION CONTROL: {'; '.join(control_list)}"
            )

        # Revealed secrets
        if self._revealed_secrets:
            # Don't list secrets, just note they're known
            constraints.append(
                f"REVEALED SECRETS ({len(self._revealed_secrets)} total): Characters know these truths"
            )

        if not constraints:
            return ""

        return "\n".join([
            "<world_state_constraints>",
            "PERMANENT WORLD CHANGES - MUST BE RESPECTED:",
            *constraints,
            "</world_state_constraints>"
        ])

    def get_context_for_location(self, location: str) -> str:
        """Get world state context specific to a location."""
        context_parts = []

        # Check if location is destroyed
        if self.is_location_destroyed(location):
            context_parts.append(f"⚠️ {location} has been DESTROYED - describe ruins/aftermath")

        # Check faction control
        faction = self.get_faction_controlling(location)
        if faction:
            context_parts.append(f"📍 {location} is controlled by {faction}")

        # Check for dead NPCs associated with location
        for entity_id, entity in self._entities.items():
            if entity.entity_type == "npc" and entity.status == EntityStatus.DEAD:
                if entity.location and entity.location.lower() == location.lower():
                    context_parts.append(f"💀 {entity.entity_id} died here")

        if not context_parts:
            return ""

        return "\n".join([
            f"[LOCATION CONTEXT: {location}]",
            *context_parts,
        ])

    def get_npc_context(self, npc_name: str) -> str:
        """Get world state context for an NPC."""
        entity = self.get_entity_state(npc_name)
        if not entity:
            return ""

        context_parts = []

        if entity.status == EntityStatus.DEAD:
            context_parts.append(f"⚠️ {npc_name} is DEAD - cannot appear alive")
            if entity.change_history:
                context_parts.append(f"Death: {entity.change_history[-1]}")
        elif entity.status == EntityStatus.CAPTURED:
            context_parts.append(f"🔒 {npc_name} is CAPTURED")
        elif entity.status == EntityStatus.MISSING:
            context_parts.append(f"❓ {npc_name} is MISSING")

        if entity.location:
            context_parts.append(f"📍 Last known location: {entity.location}")

        if entity.relationships:
            rels = [f"{k}: {v}" for k, v in list(entity.relationships.items())[:3]]
            context_parts.append(f"Relationships: {', '.join(rels)}")

        if not context_parts:
            return ""

        return "\n".join([
            f"[NPC STATE: {npc_name}]",
            *context_parts,
        ])

    # =========================================================================
    # AUTO-DETECTION FROM NARRATIVE
    # =========================================================================

    def detect_changes_from_narrative(
        self,
        narrative: str,
        active_npcs: List[str] = None,
        current_location: str = ""
    ) -> List[WorldChange]:
        """
        Detect world changes from narrative text.

        This is a helper that can be called after narrative generation
        to automatically track changes.
        """
        detected = []
        narrative_lower = narrative.lower()
        active_npcs = active_npcs or []

        # Death detection patterns
        death_patterns = [
            r"(\w+)\s+(?:was\s+)?(?:killed|slain|murdered|died|fell|perished)",
            r"(?:killed|slew|murdered)\s+(\w+)",
            r"(\w+)'s?\s+(?:last|final)\s+breath",
            r"(\w+)\s+(?:collapsed|crumpled)\s+(?:dead|lifeless)",
        ]

        for pattern in death_patterns:
            matches = re.findall(pattern, narrative_lower)
            for match in matches:
                name = match.title() if isinstance(match, str) else match[0].title()
                # Check if this is a known NPC
                if any(npc.lower() == name.lower() for npc in active_npcs):
                    if not self.is_npc_dead(name):
                        detected.append(WorldChange(
                            change_type=ChangeType.NPC_DEATH,
                            entity_id=name,
                            entity_type="npc",
                            description=f"{name} died during the scene",
                            location=current_location,
                        ))

        # Destruction detection
        destruction_patterns = [
            r"(\w+(?:\s+\w+)?)\s+(?:was\s+)?(?:destroyed|demolished|obliterated)",
            r"(?:destroyed|demolished)\s+(?:the\s+)?(\w+(?:\s+\w+)?)",
            r"(\w+(?:\s+\w+)?)\s+(?:collapsed|crumbled|exploded)",
        ]

        for pattern in destruction_patterns:
            matches = re.findall(pattern, narrative_lower)
            for match in matches:
                location = match.title() if isinstance(match, str) else match[0].title()
                if not self.is_location_destroyed(location):
                    detected.append(WorldChange(
                        change_type=ChangeType.LOCATION_DESTROYED,
                        entity_id=location,
                        entity_type="location",
                        description=f"{location} was destroyed",
                    ))

        return detected

    # =========================================================================
    # SERIALIZATION
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize engine state."""
        return {
            "entities": {k: v.to_dict() for k, v in self._entities.items()},
            "changes": [c.to_dict() for c in self._changes],
            "dead_npcs": list(self._dead_npcs),
            "destroyed_locations": list(self._destroyed_locations),
            "faction_control": self._faction_control,
            "revealed_secrets": list(self._revealed_secrets),
            "current_scene": self._current_scene,
            "current_session": self._current_session,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersistentWorldEngine":
        """Deserialize engine state."""
        engine = cls()
        engine._entities = {
            k: EntityState.from_dict(v)
            for k, v in data.get("entities", {}).items()
        }
        engine._changes = [
            WorldChange.from_dict(c)
            for c in data.get("changes", [])
        ]
        engine._dead_npcs = set(data.get("dead_npcs", []))
        engine._destroyed_locations = set(data.get("destroyed_locations", []))
        engine._faction_control = data.get("faction_control", {})
        engine._revealed_secrets = set(data.get("revealed_secrets", []))
        engine._current_scene = data.get("current_scene", 0)
        engine._current_session = data.get("current_session", "")
        return engine

    def export_campaign_state(self) -> str:
        """Export world state as human-readable summary."""
        lines = ["=" * 50, "WORLD STATE SUMMARY", "=" * 50]

        if self._dead_npcs:
            lines.append("\n## Fallen Characters")
            for npc in sorted(self._dead_npcs):
                entity = self._entities.get(npc)
                if entity and entity.change_history:
                    lines.append(f"- {npc.title()}: {entity.change_history[-1]}")
                else:
                    lines.append(f"- {npc.title()}")

        if self._destroyed_locations:
            lines.append("\n## Destroyed Locations")
            for loc in sorted(self._destroyed_locations):
                lines.append(f"- {loc.title()}")

        if self._faction_control:
            lines.append("\n## Faction Control")
            for loc, faction in sorted(self._faction_control.items()):
                lines.append(f"- {loc}: {faction}")

        if self._revealed_secrets:
            lines.append(f"\n## Secrets Revealed: {len(self._revealed_secrets)}")

        lines.append(f"\n## Total Changes Recorded: {len(self._changes)}")

        return "\n".join(lines)


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PERSISTENT WORLD ENGINE TEST")
    print("=" * 60)

    engine = PersistentWorldEngine()
    engine.set_context(scene_number=1, session_id="test_session")

    # Record some changes
    engine.record_npc_death(
        "Captain Vex",
        location="Bridge",
        caused_by="Player",
        description="Captain Vex was slain in combat"
    )

    engine.record_location_destroyed(
        "Cargo Bay Alpha",
        caused_by="Explosion",
        description="Cargo Bay Alpha was destroyed in the explosion"
    )

    engine.record_faction_control(
        "Iron Syndicate",
        "Waystation Epsilon",
        previous_faction="Independent"
    )

    engine.record_secret_revealed(
        "captain_murder",
        "The truth about the captain's death was revealed",
        revealed_by="Investigation"
    )

    # Test queries
    print("\n--- Query Tests ---")
    print(f"Is Captain Vex dead? {engine.is_npc_dead('Captain Vex')}")
    print(f"Is Cargo Bay Alpha destroyed? {engine.is_location_destroyed('Cargo Bay Alpha')}")
    print(f"Who controls Waystation Epsilon? {engine.get_faction_controlling('Waystation Epsilon')}")

    # Test narrator constraints
    print("\n--- Narrator Constraints ---")
    print(engine.get_narrator_constraints())

    # Test NPC context
    print("\n--- NPC Context ---")
    print(engine.get_npc_context("Captain Vex"))

    # Test auto-detection
    print("\n--- Auto-Detection Test ---")
    test_narrative = """
    The blade found its mark. Commander Reyes collapsed to the deck,
    her final breath a whispered curse. The command center crumbled
    around them as the station's core went critical.
    """

    detected = engine.detect_changes_from_narrative(
        test_narrative,
        active_npcs=["Commander Reyes", "Engineer Tanaka"]
    )

    for change in detected:
        print(f"Detected: {change.change_type.value} - {change.description}")

    # Export state
    print("\n--- Campaign State Export ---")
    print(engine.export_campaign_state())
