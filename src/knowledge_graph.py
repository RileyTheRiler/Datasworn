"""
Knowledge Graph for Starforged AI Game Master.
Uses NetworkX to track world state: NPCs, locations, relationships.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import networkx as nx
from networkx.readwrite import json_graph


class EntityType(str, Enum):
    """Types of entities in the game world."""
    NPC = "NPC"
    LOCATION = "LOCATION"
    ITEM = "ITEM"
    FACTION = "FACTION"
    EVENT = "EVENT"
    SHIP = "SHIP"
    VOW = "VOW"


class RelationType(str, Enum):
    """Types of relationships between entities."""
    LOCATED_AT = "located_at"
    KNOWS = "knows"
    OWNS = "owns"
    MEMBER_OF = "member_of"
    CONTROLS = "controls"
    HOSTILE_TO = "hostile_to"
    ALLIED_WITH = "allied_with"
    RELATED_TO = "related_to"


@dataclass
class Entity:
    """A world entity (node in the graph)."""
    id: str
    entity_type: EntityType
    name: str
    description: str = ""
    keywords: list[str] = field(default_factory=list)
    first_appeared: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    """A relationship between entities (edge in the graph)."""
    source_id: str
    target_id: str
    relation_type: RelationType
    description: str = ""


class GameWorldGraph:
    """
    Knowledge graph for tracking the game world.
    Uses NetworkX DiGraph for entity and relationship storage.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._entity_counter: dict[EntityType, int] = {t: 0 for t in EntityType}

    def _generate_id(self, entity_type: EntityType) -> str:
        """Generate a unique ID for a new entity."""
        self._entity_counter[entity_type] += 1
        return f"{entity_type.value.lower()}_{self._entity_counter[entity_type]:03d}"

    def add_entity(
        self,
        entity_type: EntityType,
        name: str,
        description: str = "",
        keywords: list[str] | None = None,
        first_appeared: str = "",
        **attributes,
    ) -> str:
        """
        Add a new entity to the graph.

        Args:
            entity_type: Type of entity.
            name: Display name.
            description: Free-form description.
            keywords: Keywords for lorebook matching.
            first_appeared: When/where entity was introduced.
            **attributes: Additional attributes.

        Returns:
            The generated entity ID.
        """
        entity_id = self._generate_id(entity_type)

        # Auto-generate keywords from name if not provided
        if keywords is None:
            keywords = name.lower().split()

        self.graph.add_node(
            entity_id,
            entity_type=entity_type.value,
            name=name,
            description=description,
            keywords=keywords,
            first_appeared=first_appeared,
            **attributes,
        )

        return entity_id

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        description: str = "",
    ) -> bool:
        """
        Add a relationship between two entities.

        Returns:
            True if relationship was added, False if entities don't exist.
        """
        if source_id not in self.graph or target_id not in self.graph:
            return False

        self.graph.add_edge(
            source_id,
            target_id,
            relation_type=relation_type.value,
            description=description,
        )
        return True

    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        """Get entity data by ID."""
        if entity_id in self.graph:
            return dict(self.graph.nodes[entity_id])
        return None

    def find_entity_by_name(self, name: str) -> str | None:
        """Find entity ID by name (case-insensitive)."""
        name_lower = name.lower()
        for node_id, data in self.graph.nodes(data=True):
            if data.get("name", "").lower() == name_lower:
                return node_id
        return None

    def get_entities_by_type(self, entity_type: EntityType) -> list[dict[str, Any]]:
        """Get all entities of a specific type."""
        return [
            {"id": node_id, **data}
            for node_id, data in self.graph.nodes(data=True)
            if data.get("entity_type") == entity_type.value
        ]

    def get_npcs_at_location(self, location_id: str) -> list[dict[str, Any]]:
        """Get all NPCs at a specific location."""
        npcs = []
        for edge_source, edge_target, edge_data in self.graph.edges(data=True):
            if (
                edge_target == location_id
                and edge_data.get("relation_type") == RelationType.LOCATED_AT.value
            ):
                entity = self.get_entity(edge_source)
                if entity and entity.get("entity_type") == EntityType.NPC.value:
                    npcs.append({"id": edge_source, **entity})
        return npcs

    def get_related_entities(
        self, entity_id: str, relation_type: RelationType | None = None
    ) -> list[dict[str, Any]]:
        """Get entities related to the given entity."""
        related = []

        # Outgoing relationships
        for _, target, data in self.graph.out_edges(entity_id, data=True):
            if relation_type is None or data.get("relation_type") == relation_type.value:
                entity = self.get_entity(target)
                if entity:
                    related.append({"id": target, "relation": data, **entity})

        # Incoming relationships
        for source, _, data in self.graph.in_edges(entity_id, data=True):
            if relation_type is None or data.get("relation_type") == relation_type.value:
                entity = self.get_entity(source)
                if entity:
                    related.append({"id": source, "relation": data, **entity})

        return related

    def search_by_keyword(self, keyword: str) -> list[dict[str, Any]]:
        """Search entities by keyword."""
        keyword_lower = keyword.lower()
        results = []
        for node_id, data in self.graph.nodes(data=True):
            keywords = data.get("keywords", [])
            if keyword_lower in keywords or keyword_lower in data.get("name", "").lower():
                results.append({"id": node_id, **data})
        return results

    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity and all its relationships."""
        if entity_id in self.graph:
            self.graph.remove_node(entity_id)
            return True
        return False

    # ========================================================================
    # Serialization
    # ========================================================================

    def save_to_json(self, filepath: str | Path) -> None:
        """Save the graph to a JSON file."""
        data = json_graph.node_link_data(self.graph)
        data["_entity_counter"] = {k.value: v for k, v in self._entity_counter.items()}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_json(self, filepath: str | Path) -> None:
        """Load the graph from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        counter_data = data.pop("_entity_counter", {})
        self._entity_counter = {
            EntityType(k): v for k, v in counter_data.items()
        }

        self.graph = json_graph.node_link_graph(data)

    # ========================================================================
    # Lorebook System
    # ========================================================================

    def get_relevant_context(
        self,
        recent_messages: list[str],
        token_budget: int = 800,
    ) -> str:
        """
        Get relevant world information based on recent messages.
        Implements keyword-triggered context injection (lorebook).

        Args:
            recent_messages: List of recent message contents.
            token_budget: Approximate character budget (~4 chars per token).

        Returns:
            Formatted lorebook entries.
        """
        # Extract keywords from recent messages
        message_text = " ".join(recent_messages).lower()
        words = set(message_text.split())

        # Find matching entities
        matches = []
        for node_id, data in self.graph.nodes(data=True):
            keywords = data.get("keywords", [])
            name_words = data.get("name", "").lower().split()

            score = 0
            for kw in keywords + name_words:
                if kw in words:
                    score += 1

            if score > 0:
                matches.append((score, node_id, data))

        # Sort by relevance
        matches.sort(key=lambda x: x[0], reverse=True)

        # Build lorebook entries within budget
        entries = []
        char_count = 0
        char_budget = token_budget * 4

        for _, node_id, data in matches:
            entry = self._format_lorebook_entry(node_id, data)
            if char_count + len(entry) <= char_budget:
                entries.append(entry)
                char_count += len(entry)
            else:
                break

        if entries:
            return "[World Information]\n" + "\n\n".join(entries) + "\n[End World Information]"
        return ""

    def _format_lorebook_entry(self, entity_id: str, data: dict) -> str:
        """Format a single lorebook entry."""
        entity_type = data.get("entity_type", "UNKNOWN")
        name = data.get("name", "Unknown")
        description = data.get("description", "")

        lines = [f"[{entity_type}: {name}]"]
        if description:
            lines.append(description)

        # Add relationships
        relations = []
        for _, target, edge_data in self.graph.out_edges(entity_id, data=True):
            target_data = self.get_entity(target)
            if target_data:
                rel_type = edge_data.get("relation_type", "related_to")
                relations.append(f"{rel_type} {target_data.get('name', target)}")

        if relations:
            lines.append("Relationships: " + ", ".join(relations))

        return "\n".join(lines)

    def build_context_block(self, recent_messages: list[str]) -> str:
        """
        Build a complete context block for the narrator.
        Alias for get_relevant_context with default budget.
        """
        return self.get_relevant_context(recent_messages)


# ============================================================================
# Entity Extraction (placeholder for LLM-based extraction)
# ============================================================================

def extract_entities_from_text(
    narrative_text: str,
    world_graph: GameWorldGraph,
) -> list[str]:
    """
    Extract and add entities mentioned in narrative text.
    This is a simple pattern-based implementation.
    For better results, use LLM-based extraction.

    Args:
        narrative_text: The narrative to analyze.
        world_graph: The world graph to check against/update.

    Returns:
        List of new entity IDs created.
    """
    import re

    new_entities = []

    # Simple patterns for common entities (to be enhanced with LLM)
    # Look for capitalized words that might be names
    potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', narrative_text)

    for name in potential_names:
        # Skip common words
        if name.lower() in {"the", "you", "your", "they", "their", "this", "that"}:
            continue

        # Check if entity already exists
        if world_graph.find_entity_by_name(name):
            continue

        # Determine entity type based on context (simplified heuristic)
        text_lower = narrative_text.lower()
        name_lower = name.lower()

        if any(word in text_lower for word in ["station", "planet", "sector", "port", "settlement"]):
            if name_lower in text_lower:
                # Might be a location
                entity_id = world_graph.add_entity(
                    EntityType.LOCATION,
                    name,
                    description=f"A location mentioned in the narrative.",
                )
                new_entities.append(entity_id)
        elif any(word in text_lower for word in ["said", "replied", "spoke", "she", "he", "they"]):
            if name_lower in text_lower:
                # Might be an NPC
                entity_id = world_graph.add_entity(
                    EntityType.NPC,
                    name,
                    description=f"An NPC encountered in the narrative.",
                )
                new_entities.append(entity_id)

    return new_entities


# ============================================================================
# Consequence Engine
# ============================================================================

@dataclass
class ConsequenceEvent:
    """Represents an event that should propagate consequences."""
    event_type: str  # "kill", "ally", "betray", "discover", "complete_vow", etc.
    source_entity: str  # Entity taking action
    target_entity: str  # Entity affected
    description: str
    session_number: int = 0


@dataclass
class DelayedBeat:
    """A dramatic beat queued for future triggering."""
    beat: str
    trigger_after_scenes: int
    priority: int = 5  # 1-10, higher = more important
    related_entities: list[str] = field(default_factory=list)


class ConsequenceEngine:
    """
    Propagates consequences of events through the world graph.
    Integrates with Director for narrative pacing.
    """
    
    def __init__(self, world_graph: GameWorldGraph):
        self.graph = world_graph
        self.delayed_beats: list[DelayedBeat] = []
        self.moral_patterns: list[str] = []  # Track player's moral choices
        self.scene_count: int = 0
    
    def propagate_consequences(self, event: ConsequenceEvent) -> list[DelayedBeat]:
        """
        Propagate an event's consequences through the world.
        
        Returns:
            List of new beats queued for the Director
        """
        new_beats = []
        
        # Immediate: Update entity states
        self._apply_immediate_consequences(event)
        
        # Local: Affect connected entities
        local_beats = self._propagate_local(event)
        new_beats.extend(local_beats)
        
        # Delayed: Queue future complications
        delayed_beats = self._generate_delayed_consequences(event)
        self.delayed_beats.extend(delayed_beats)
        new_beats.extend(delayed_beats)
        
        # Track moral patterns
        self._track_moral_pattern(event)
        
        return new_beats
    
    def _apply_immediate_consequences(self, event: ConsequenceEvent) -> None:
        """Apply immediate state changes to entities."""
        target = self.graph.get_entity(event.target_entity)
        if not target:
            return
        
        # Update target based on event type
        if event.event_type == "kill":
            # Mark as dead
            self.graph.graph.nodes[event.target_entity]["status"] = "dead"
            
        elif event.event_type == "ally":
            # Improve relationship
            self.graph.add_relationship(
                event.source_entity,
                event.target_entity,
                RelationType.ALLIED_WITH,
                event.description
            )
            
        elif event.event_type == "betray":
            # Create hostile relationship
            self.graph.add_relationship(
                event.target_entity,
                event.source_entity,
                RelationType.HOSTILE_TO,
                f"Betrayed: {event.description}"
            )
    
    def _propagate_local(self, event: ConsequenceEvent) -> list[DelayedBeat]:
        """Propagate effects to connected entities."""
        beats = []
        
        # Get entities related to the target
        related = self.graph.get_related_entities(event.target_entity)
        
        for entity in related:
            entity_type = entity.get("entity_type")
            relation = entity.get("relation", {})
            
            # Factions react to member events
            if entity_type == EntityType.FACTION.value:
                if event.event_type == "kill":
                    # Faction seeks revenge
                    beats.append(DelayedBeat(
                        beat=f"{entity['name']} seeks revenge for {event.description}",
                        trigger_after_scenes=2,
                        priority=7,
                        related_entities=[entity["id"], event.source_entity]
                    ))
                    
            # NPCs react to ally events
            elif entity_type == EntityType.NPC.value:
                if event.event_type == "betray":
                    # Other NPCs hear about betrayal
                    beats.append(DelayedBeat(
                        beat=f"{entity['name']} hears about the betrayal and questions trust",
                        trigger_after_scenes=3,
                        priority=5,
                        related_entities=[entity["id"]]
                    ))
        
        return beats
    
    def _generate_delayed_consequences(self, event: ConsequenceEvent) -> list[DelayedBeat]:
        """Generate delayed consequences for the Director."""
        beats = []
        
        if event.event_type == "kill":
            # Someone wants revenge
            beats.append(DelayedBeat(
                beat=f"Someone connected to {event.target_entity} seeks answers or revenge",
                trigger_after_scenes=4,
                priority=6,
            ))
            
        elif event.event_type == "spare":
            # The spared may return
            beats.append(DelayedBeat(
                beat=f"The one you spared returns—friend or foe remains to be seen",
                trigger_after_scenes=5,
                priority=5,
            ))
            
        elif event.event_type == "discover":
            # Discovery has ripple effects
            beats.append(DelayedBeat(
                beat=f"Others learn of the discovery: {event.description}",
                trigger_after_scenes=3,
                priority=4,
            ))
        
        return beats
    
    def _track_moral_pattern(self, event: ConsequenceEvent) -> None:
        """Track player's moral choices for pattern analysis."""
        moral_events = ["kill", "spare", "betray", "ally", "sacrifice", "abandon"]
        
        if event.event_type in moral_events:
            pattern = f"{event.event_type}: {event.description}"
            self.moral_patterns.append(pattern)
            
            # Keep last 10 patterns
            if len(self.moral_patterns) > 10:
                self.moral_patterns.pop(0)
    
    def get_due_beats(self) -> list[DelayedBeat]:
        """Get beats that should trigger now and remove them from queue."""
        due = [b for b in self.delayed_beats if b.trigger_after_scenes <= 0]
        self.delayed_beats = [b for b in self.delayed_beats if b.trigger_after_scenes > 0]
        return sorted(due, key=lambda x: x.priority, reverse=True)
    
    def advance_scene(self) -> None:
        """Called when a scene ends. Decrements beat timers."""
        self.scene_count += 1
        for beat in self.delayed_beats:
            beat.trigger_after_scenes -= 1
    
    def get_moral_analysis(self) -> str:
        """Analyze moral patterns for Director use."""
        if not self.moral_patterns:
            return "No significant moral choices yet."
        
        # Count types
        kills = sum(1 for p in self.moral_patterns if p.startswith("kill"))
        spares = sum(1 for p in self.moral_patterns if p.startswith("spare"))
        betrayals = sum(1 for p in self.moral_patterns if p.startswith("betray"))
        alliances = sum(1 for p in self.moral_patterns if p.startswith("ally"))
        
        analysis = []
        if kills > spares:
            analysis.append("Tends toward pragmatic violence")
        elif spares > kills:
            analysis.append("Shows mercy when possible")
        
        if betrayals > alliances:
            analysis.append("Breaks promises when convenient")
        elif alliances > 0:
            analysis.append("Values building connections")
        
        return "; ".join(analysis) if analysis else "Mixed moral approach"


# ============================================================================
# Vow as Dramatic Engine
# ============================================================================

@dataclass
class VowTracker:
    """
    Enhanced vow tracking for dramatic pacing.
    Vows are the sacred heart of Ironsworn/Starforged.
    """
    vow_id: str
    name: str
    rank: str  # troublesome, dangerous, formidable, extreme, epic
    ticks: int = 0  # 0-40, 10 boxes of 4 ticks
    
    # Narrative tracking
    stakes: str = ""  # What's at risk
    complications: list[str] = field(default_factory=list)
    sacrifices: list[str] = field(default_factory=list)
    
    @property
    def progress_percent(self) -> float:
        """Progress as 0.0 - 1.0"""
        return self.ticks / 40.0
    
    @property
    def phase(self) -> str:
        """Dramatic phase based on progress."""
        pct = self.progress_percent
        if pct < 0.25:
            return "establishing"  # Stakes being set
        elif pct < 0.50:
            return "developing"  # Complications arise
        elif pct < 0.75:
            return "escalating"  # Stakes at their highest
        elif pct < 1.0:
            return "approaching_climax"  # Final push
        else:
            return "ready_for_resolution"
    
    def get_director_guidance(self) -> dict:
        """Get pacing/tone guidance based on vow phase."""
        phase = self.phase
        
        guidance = {
            "establishing": {
                "pacing": "standard",
                "tone": "mysterious",
                "notes": f"Establish what's at stake with vow '{self.name}'. Show why it matters."
            },
            "developing": {
                "pacing": "standard", 
                "tone": "ominous",
                "notes": f"Introduce complications for '{self.name}'. The path should not be easy."
            },
            "escalating": {
                "pacing": "fast",
                "tone": "tense",
                "notes": f"Escalate stakes for '{self.name}'. Force hard choices. What must be sacrificed?"
            },
            "approaching_climax": {
                "pacing": "fast",
                "tone": "tense",
                "notes": f"Build to climax of '{self.name}'. Maximum tension. No turning back."
            },
            "ready_for_resolution": {
                "pacing": "standard",
                "tone": "triumphant",
                "notes": f"Vow '{self.name}' ready for resolution. Catharsis—but at what cost?"
            }
        }
        
        return guidance.get(phase, guidance["establishing"])
    
    def add_complication(self, complication: str) -> None:
        """Record a complication encountered."""
        self.complications.append(complication)
    
    def add_sacrifice(self, sacrifice: str) -> None:
        """Record something sacrificed for this vow."""
        self.sacrifices.append(sacrifice)
    
    def to_dict(self) -> dict:
        return {
            "vow_id": self.vow_id,
            "name": self.name,
            "rank": self.rank,
            "ticks": self.ticks,
            "stakes": self.stakes,
            "complications": self.complications,
            "sacrifices": self.sacrifices,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VowTracker":
        return cls(
            vow_id=data.get("vow_id", ""),
            name=data.get("name", "Unknown Vow"),
            rank=data.get("rank", "dangerous"),
            ticks=data.get("ticks", 0),
            stakes=data.get("stakes", ""),
            complications=data.get("complications", []),
            sacrifices=data.get("sacrifices", []),
        )


class VowManager:
    """Manages vows and their dramatic integration."""
    
    def __init__(self):
        self.vows: dict[str, VowTracker] = {}
        self._vow_counter = 0
    
    def create_vow(self, name: str, rank: str, stakes: str = "") -> VowTracker:
        """Create a new vow."""
        self._vow_counter += 1
        vow_id = f"vow_{self._vow_counter:03d}"
        
        vow = VowTracker(
            vow_id=vow_id,
            name=name,
            rank=rank,
            stakes=stakes,
        )
        self.vows[vow_id] = vow
        return vow
    
    def get_active_vows(self) -> list[VowTracker]:
        """Get all active (incomplete) vows."""
        return [v for v in self.vows.values() if v.ticks < 40]
    
    def get_primary_vow(self) -> VowTracker | None:
        """Get the vow with highest progress (most dramatic tension)."""
        active = self.get_active_vows()
        if not active:
            return None
        return max(active, key=lambda v: v.progress_percent)
    
    def get_combined_director_guidance(self) -> dict:
        """Get combined guidance from all active vows."""
        primary = self.get_primary_vow()
        if not primary:
            return {"pacing": "standard", "tone": "mysterious", "notes": "No active vows."}
        
        return primary.get_director_guidance()
    
    def forsake_vow(self, vow_id: str) -> list[DelayedBeat]:
        """
        Mark a vow as forsaken. This is dramatic gold.
        Returns beats for the Director.
        """
        vow = self.vows.get(vow_id)
        if not vow:
            return []
        
        # Remove from active vows
        del self.vows[vow_id]
        
        # Generate dramatic consequences
        return [
            DelayedBeat(
                beat=f"The weight of the forsaken vow '{vow.name}' haunts you",
                trigger_after_scenes=1,
                priority=8,
            ),
            DelayedBeat(
                beat=f"Someone reminds you of what you abandoned: '{vow.name}'",
                trigger_after_scenes=4,
                priority=6,
            ),
        ]
    
    def to_dict(self) -> dict:
        return {
            "vows": {vid: v.to_dict() for vid, v in self.vows.items()},
            "_vow_counter": self._vow_counter,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VowManager":
        manager = cls()
        manager._vow_counter = data.get("_vow_counter", 0)
        for vid, vdata in data.get("vows", {}).items():
            manager.vows[vid] = VowTracker.from_dict(vdata)
        return manager


# ============================================================================
# Influence Maps & Territory System
# ============================================================================

@dataclass
class ZoneInfluence:
    """Influence a faction has over a specific zone."""
    faction_id: str
    faction_name: str
    strength: float = 0.5  # 0-1, how much control they have
    stability: float = 0.5  # 0-1, how stable that control is
    last_contested: int = 0  # Scene number when last contested


# ============================================================================
# Tactical Terrain System
# ============================================================================

class TerrainFeature(str, Enum):
    """Types of terrain features that affect combat."""
    CHOKEPOINT = "chokepoint"  # Narrow passage, limits flanking
    COVER = "cover"  # Reduces incoming damage
    HIGH_GROUND = "high_ground"  # Range/accuracy advantage
    STRONGHOLD = "stronghold"  # Defensive fortification
    HAZARD = "hazard"  # Environmental danger
    OPEN = "open"  # No tactical advantage
    AMBUSH_POINT = "ambush_point"  # Good for surprise attacks
    ESCAPE_ROUTE = "escape_route"  # Easy retreat path


@dataclass
class TacticalPoint:
    """A specific tactical location within a zone."""
    name: str
    feature: TerrainFeature
    defense_bonus: float = 0.0  # -1 to 1, negative = exposed
    attack_bonus: float = 0.0  # -1 to 1
    movement_cost: float = 1.0  # Multiplier, >1 = slower
    capacity: int = 3  # How many units can use this point
    description: str = ""
    
    def get_combat_modifier(self) -> dict:
        """Get combat modifiers for units at this point."""
        return {
            "defense": self.defense_bonus,
            "attack": self.attack_bonus,
            "description": self.get_tactical_description(),
        }
    
    def get_tactical_description(self) -> str:
        """Generate narrative description of tactical advantage."""
        descs = {
            TerrainFeature.CHOKEPOINT: "The narrow passage limits enemy numbers",
            TerrainFeature.COVER: "Solid cover reduces incoming fire",
            TerrainFeature.HIGH_GROUND: "The elevated position grants clear sight lines",
            TerrainFeature.STRONGHOLD: "Fortified walls provide excellent protection",
            TerrainFeature.HAZARD: "The environmental hazard threatens everyone",
            TerrainFeature.OPEN: "No cover - exposed to all angles",
            TerrainFeature.AMBUSH_POINT: "Perfect concealment for a surprise attack",
            TerrainFeature.ESCAPE_ROUTE: "A clear path to retreat if needed",
        }
        return self.description or descs.get(self.feature, "Tactical position")


# Pre-built tactical points for common scenarios
TACTICAL_PRESETS = {
    "corridor": TacticalPoint(
        name="Corridor",
        feature=TerrainFeature.CHOKEPOINT,
        defense_bonus=0.3,
        attack_bonus=-0.1,
        capacity=2,
        description="A narrow corridor - they can only come at you two at a time",
    ),
    "barricade": TacticalPoint(
        name="Barricade",
        feature=TerrainFeature.COVER,
        defense_bonus=0.4,
        attack_bonus=0.0,
        capacity=4,
        description="Makeshift barricade provides solid cover",
    ),
    "watchtower": TacticalPoint(
        name="Watchtower",
        feature=TerrainFeature.HIGH_GROUND,
        defense_bonus=0.2,
        attack_bonus=0.3,
        capacity=2,
        description="Elevated position with clear sight lines",
    ),
    "bunker": TacticalPoint(
        name="Bunker",
        feature=TerrainFeature.STRONGHOLD,
        defense_bonus=0.6,
        attack_bonus=0.1,
        capacity=6,
        description="Reinforced bunker - nearly impervious",
    ),
    "reactor_room": TacticalPoint(
        name="Reactor Room",
        feature=TerrainFeature.HAZARD,
        defense_bonus=-0.2,
        attack_bonus=-0.2,
        movement_cost=1.5,
        description="Radiation and unstable equipment threaten all combatants",
    ),
    "cargo_bay": TacticalPoint(
        name="Cargo Bay",
        feature=TerrainFeature.OPEN,
        defense_bonus=-0.3,
        attack_bonus=0.0,
        capacity=20,
        description="Wide open space - nowhere to hide",
    ),
    "maintenance_shaft": TacticalPoint(
        name="Maintenance Shaft",
        feature=TerrainFeature.AMBUSH_POINT,
        defense_bonus=0.1,
        attack_bonus=0.4,
        capacity=3,
        description="Dark corners and blind spots - perfect for an ambush",
    ),
    "airlock": TacticalPoint(
        name="Airlock",
        feature=TerrainFeature.ESCAPE_ROUTE,
        defense_bonus=-0.1,
        attack_bonus=0.0,
        description="Quick exit to the void if things go wrong",
    ),
}


@dataclass
class Zone:
    """A zone/location in the influence map."""
    zone_id: str
    name: str
    zone_type: str = "neutral"  # outpost, station, planet, asteroid, debris
    influences: dict[str, ZoneInfluence] = field(default_factory=dict)
    threat_level: float = 0.0  # 0-1 overall danger
    resources: float = 0.5  # 0-1 strategic value
    connected_zones: list[str] = field(default_factory=list)
    
    # Tactical terrain features
    tactical_points: list[TacticalPoint] = field(default_factory=list)
    primary_terrain: TerrainFeature = TerrainFeature.OPEN
    
    @property
    def controlling_faction(self) -> str | None:
        """Returns the faction with highest influence, if any has >0.5"""
        if not self.influences:
            return None
        strongest = max(self.influences.values(), key=lambda i: i.strength)
        return strongest.faction_name if strongest.strength > 0.5 else None
    
    @property
    def is_contested(self) -> bool:
        """Returns True if multiple factions have significant presence."""
        significant = [i for i in self.influences.values() if i.strength > 0.25]
        return len(significant) > 1
    
    @property
    def best_defensive_point(self) -> TacticalPoint | None:
        """Get the best defensive position in this zone."""
        if not self.tactical_points:
            return None
        return max(self.tactical_points, key=lambda p: p.defense_bonus)
    
    @property
    def best_attack_point(self) -> TacticalPoint | None:
        """Get the best offensive position in this zone."""
        if not self.tactical_points:
            return None
        return max(self.tactical_points, key=lambda p: p.attack_bonus)
    
    def get_tactical_context(self) -> str:
        """Generate tactical context for combat narration."""
        lines = [f"[TERRAIN: {self.name}]"]
        
        # Primary terrain
        terrain_effects = {
            TerrainFeature.CHOKEPOINT: "Chokepoint limits enemy numbers",
            TerrainFeature.COVER: "Cover available for defense",
            TerrainFeature.HIGH_GROUND: "Height advantage possible",
            TerrainFeature.STRONGHOLD: "Fortified position",
            TerrainFeature.HAZARD: "Environmental hazard present",
            TerrainFeature.OPEN: "Open ground - no cover",
            TerrainFeature.AMBUSH_POINT: "Ambush opportunities",
            TerrainFeature.ESCAPE_ROUTE: "Retreat route available",
        }
        lines.append(f"Type: {terrain_effects.get(self.primary_terrain, 'Standard')}")
        
        # Best positions
        if self.tactical_points:
            best_def = self.best_defensive_point
            best_atk = self.best_attack_point
            if best_def:
                lines.append(f"Defensive: {best_def.name} (+{best_def.defense_bonus:.0%})")
            if best_atk and best_atk != best_def:
                lines.append(f"Offensive: {best_atk.name} (+{best_atk.attack_bonus:.0%})")
        
        return "\n".join(lines)
    
    def add_tactical_point(self, preset: str) -> TacticalPoint | None:
        """Add a preset tactical point to this zone."""
        if preset in TACTICAL_PRESETS:
            point = TacticalPoint(**TACTICAL_PRESETS[preset].__dict__)
            self.tactical_points.append(point)
            return point
        return None


class InfluenceMap:
    """
    Tracks faction influence across zones in the game world.
    Used for strategic AI decisions and narrative context.
    """
    
    def __init__(self):
        self.zones: dict[str, Zone] = {}
        self.factions: dict[str, dict] = {}  # faction_id -> {name, disposition, etc}
        self._zone_counter = 0
    
    def add_faction(self, faction_id: str, name: str, disposition: str = "neutral") -> None:
        """Register a faction in the system."""
        self.factions[faction_id] = {
            "name": name,
            "disposition": disposition,  # friendly, neutral, hostile
            "total_zones": 0,
        }
    
    def add_zone(
        self, 
        name: str, 
        zone_type: str = "neutral",
        resources: float = 0.5,
        connected_to: list[str] | None = None,
    ) -> str:
        """Add a new zone to the map."""
        self._zone_counter += 1
        zone_id = f"zone_{self._zone_counter:03d}"
        
        self.zones[zone_id] = Zone(
            zone_id=zone_id,
            name=name,
            zone_type=zone_type,
            resources=resources,
            connected_zones=connected_to or [],
        )
        return zone_id
    
    def set_influence(
        self,
        zone_id: str,
        faction_id: str,
        strength: float,
        stability: float = 0.5,
    ) -> None:
        """Set a faction's influence in a zone."""
        if zone_id not in self.zones:
            return
        if faction_id not in self.factions:
            return
        
        zone = self.zones[zone_id]
        faction = self.factions[faction_id]
        
        zone.influences[faction_id] = ZoneInfluence(
            faction_id=faction_id,
            faction_name=faction["name"],
            strength=max(0.0, min(1.0, strength)),
            stability=max(0.0, min(1.0, stability)),
        )
        
        # Update faction's zone count
        self._recalculate_faction_territory()
    
    def _recalculate_faction_territory(self) -> None:
        """Recalculate total zones controlled by each faction."""
        for faction_id in self.factions:
            self.factions[faction_id]["total_zones"] = 0
        
        for zone in self.zones.values():
            controller = zone.controlling_faction
            if controller:
                for faction_id, faction in self.factions.items():
                    if faction["name"] == controller:
                        faction["total_zones"] += 1
    
    def contest_zone(
        self,
        zone_id: str,
        attacking_faction: str,
        attack_strength: float,
        scene_number: int,
    ) -> dict:
        """
        Simulate a faction contesting a zone.
        
        Returns:
            Dict with result of the contest
        """
        if zone_id not in self.zones:
            return {"success": False, "reason": "Zone not found"}
        
        zone = self.zones[zone_id]
        
        # Get or create attacker influence
        if attacking_faction not in zone.influences:
            faction_name = self.factions.get(attacking_faction, {}).get("name", "Unknown")
            zone.influences[attacking_faction] = ZoneInfluence(
                faction_id=attacking_faction,
                faction_name=faction_name,
                strength=0.0,
                stability=0.0,
            )
        
        attacker = zone.influences[attacking_faction]
        
        # Reduce other factions' influence
        for faction_id, influence in zone.influences.items():
            if faction_id != attacking_faction:
                reduction = attack_strength * 0.3
                influence.strength = max(0.0, influence.strength - reduction)
                influence.stability = max(0.0, influence.stability - reduction * 0.5)
        
        # Increase attacker influence
        attacker.strength = min(1.0, attacker.strength + attack_strength * 0.4)
        attacker.last_contested = scene_number
        
        # Update threat level
        zone.threat_level = min(1.0, zone.threat_level + 0.2)
        
        self._recalculate_faction_territory()
        
        return {
            "success": True,
            "new_controller": zone.controlling_faction,
            "is_contested": zone.is_contested,
            "threat_level": zone.threat_level,
        }
    
    def calculate_zone_threat(self, zone_id: str) -> float:
        """Calculate threat level based on faction conflicts and stability."""
        if zone_id not in self.zones:
            return 0.0
        
        zone = self.zones[zone_id]
        
        # Base threat from contested status
        threat = 0.2 if zone.is_contested else 0.0
        
        # Add threat from unstable factions
        for influence in zone.influences.values():
            if influence.stability < 0.3:
                threat += 0.2 * (1 - influence.stability)
        
        # Add threat from hostile factions
        for faction_id, influence in zone.influences.items():
            faction = self.factions.get(faction_id, {})
            if faction.get("disposition") == "hostile" and influence.strength > 0.3:
                threat += 0.3 * influence.strength
        
        zone.threat_level = min(1.0, threat)
        return zone.threat_level
    
    def get_zone_context(self, zone_id: str) -> str:
        """Get narrative context for a zone."""
        if zone_id not in self.zones:
            return ""
        
        zone = self.zones[zone_id]
        lines = [f"[ZONE: {zone.name}]"]
        
        controller = zone.controlling_faction
        if controller:
            lines.append(f"Controlled by: {controller}")
        elif zone.is_contested:
            lines.append("Status: Contested territory")
        else:
            lines.append("Status: Neutral/unclaimed")
        
        if zone.threat_level > 0.7:
            lines.append("Danger: EXTREME")
        elif zone.threat_level > 0.4:
            lines.append("Danger: HIGH")
        elif zone.threat_level > 0.2:
            lines.append("Danger: MODERATE")
        
        if zone.influences:
            factions = [f"{i.faction_name} ({i.strength:.0%})" 
                       for i in zone.influences.values() if i.strength > 0.1]
            if factions:
                lines.append(f"Factions: {', '.join(factions)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "zones": {
                zid: {
                    "name": z.name,
                    "zone_type": z.zone_type,
                    "threat_level": z.threat_level,
                    "resources": z.resources,
                    "connected_zones": z.connected_zones,
                    "influences": {
                        fid: {
                            "faction_name": inf.faction_name,
                            "strength": inf.strength,
                            "stability": inf.stability,
                        }
                        for fid, inf in z.influences.items()
                    },
                }
                for zid, z in self.zones.items()
            },
            "factions": self.factions,
            "_zone_counter": self._zone_counter,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InfluenceMap":
        imap = cls()
        imap.factions = data.get("factions", {})
        imap._zone_counter = data.get("_zone_counter", 0)
        
        for zid, zdata in data.get("zones", {}).items():
            zone = Zone(
                zone_id=zid,
                name=zdata.get("name", "Unknown"),
                zone_type=zdata.get("zone_type", "neutral"),
                threat_level=zdata.get("threat_level", 0.0),
                resources=zdata.get("resources", 0.5),
                connected_zones=zdata.get("connected_zones", []),
            )
            for fid, infdata in zdata.get("influences", {}).items():
                zone.influences[fid] = ZoneInfluence(
                    faction_id=fid,
                    faction_name=infdata.get("faction_name", "Unknown"),
                    strength=infdata.get("strength", 0.0),
                    stability=infdata.get("stability", 0.5),
                )
            imap.zones[zid] = zone
        
        return imap

