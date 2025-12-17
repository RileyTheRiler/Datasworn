"""
Social Memory System - Witcher III-tier Social Consequence.
Implements history stacks, vendetta detection, and memory fallibility.

"You killed my brother!" - Emergent consequence from social graph.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random
import math


# ============================================================================
# History Stack System
# ============================================================================

class EventType(Enum):
    """Types of social events that get recorded."""
    HELPED = "helped"
    BETRAYED = "betrayed"
    STOLE_FROM = "stole_from"
    KILLED = "killed"
    SAVED = "saved"
    LIED_TO = "lied_to"
    KEPT_PROMISE = "kept_promise"
    BROKE_PROMISE = "broke_promise"
    INSULTED = "insulted"
    COMPLIMENTED = "complimented"
    BRIBED = "bribed"
    THREATENED = "threatened"
    PROTECTED = "protected"
    WITNESSED = "witnessed"  # Saw something happen


@dataclass
class HistoryElement:
    """A single recorded social event."""
    event_type: EventType
    target: str  # Who was affected
    actor: str  # Who did it
    context: str  # What happened
    relationship_delta: int  # Change to relationship (-100 to +100)
    timestamp: int  # Scene/day number
    location: str = ""
    witnesses: list[str] = field(default_factory=list)
    is_public: bool = False  # Known to everyone?
    decay_rate: float = 0.1  # How fast this memory fades


class SocialHistoryStack:
    """
    Stack of specific events between entities.
    Not just "Trust: 45" but WHY it's 45.
    """
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.events: list[HistoryElement] = []
        self.max_events: int = 50  # Memory limit
    
    def record_event(
        self,
        event_type: EventType,
        target: str,
        actor: str,
        context: str,
        relationship_delta: int,
        timestamp: int,
        witnesses: list[str] = None,
    ) -> HistoryElement:
        """Record a new social event."""
        event = HistoryElement(
            event_type=event_type,
            target=target,
            actor=actor,
            context=context,
            relationship_delta=relationship_delta,
            timestamp=timestamp,
            witnesses=witnesses or [],
        )
        
        self.events.append(event)
        
        # Trim old events if over limit
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        return event
    
    def get_relationship_score(self, with_entity: str) -> int:
        """Calculate total relationship based on history."""
        score = 0
        for event in self.events:
            if event.target == with_entity or event.actor == with_entity:
                score += event.relationship_delta
        return max(-100, min(100, score))
    
    def get_events_involving(self, entity: str) -> list[HistoryElement]:
        """Get all events involving a specific entity."""
        return [e for e in self.events if e.target == entity or e.actor == entity]
    
    def get_events_of_type(self, event_type: EventType) -> list[HistoryElement]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def has_vendetta_trigger(self, against: str) -> HistoryElement | None:
        """Check if there's a vendetta-worthy event against someone."""
        vendetta_types = [EventType.KILLED, EventType.BETRAYED]
        for event in reversed(self.events):  # Most recent first
            if event.actor == against and event.event_type in vendetta_types:
                return event
        return None
    
    def get_narrative_context(self) -> str:
        """Generate context for narrator about this entity's history."""
        if not self.events:
            return ""
        
        lines = [f"[SOCIAL HISTORY: {self.entity_id}]"]
        
        # Group by relationship
        relationships = {}
        for event in self.events:
            other = event.target if event.actor == self.entity_id else event.actor
            if other not in relationships:
                relationships[other] = []
            relationships[other].append(event)
        
        for other, events in list(relationships.items())[:3]:
            score = sum(e.relationship_delta for e in events)
            recent = events[-1]
            lines.append(f"• {other}: {score:+d} (last: {recent.event_type.value} - {recent.context[:30]})")
        
        return "\n".join(lines)


# ============================================================================
# Vendetta Detection System
# ============================================================================

class RelationType(Enum):
    """Types of relationships for vendetta calculation."""
    FAMILY = "family"  # Blood relation
    LOVER = "lover"
    FRIEND = "friend"
    ALLY = "ally"
    FACTION_MEMBER = "faction_member"
    EMPLOYER = "employer"
    RIVAL = "rival"


@dataclass
class SocialLink:
    """A relationship between two entities."""
    entity_a: str
    entity_b: str
    relation_type: RelationType
    strength: float = 1.0  # 0-1


class SocialGraph:
    """
    Graph of social relationships for vendetta detection.
    When player kills X, query for X's family → auto-create grudges.
    """
    
    def __init__(self):
        self.links: list[SocialLink] = []
        self.histories: dict[str, SocialHistoryStack] = {}
    
    def add_link(
        self,
        entity_a: str,
        entity_b: str,
        relation_type: RelationType,
        strength: float = 1.0,
    ) -> None:
        """Add a social link between entities."""
        link = SocialLink(
            entity_a=entity_a,
            entity_b=entity_b,
            relation_type=relation_type,
            strength=strength,
        )
        self.links.append(link)
    
    def get_relations(self, entity: str) -> list[tuple[str, SocialLink]]:
        """Get all entities related to this one."""
        relations = []
        for link in self.links:
            if link.entity_a == entity:
                relations.append((link.entity_b, link))
            elif link.entity_b == entity:
                relations.append((link.entity_a, link))
        return relations
    
    def get_family(self, entity: str) -> list[str]:
        """Get family members of an entity."""
        family = []
        for other, link in self.get_relations(entity):
            if link.relation_type == RelationType.FAMILY:
                family.append(other)
        return family
    
    def get_history(self, entity: str) -> SocialHistoryStack:
        """Get or create history stack for an entity."""
        if entity not in self.histories:
            self.histories[entity] = SocialHistoryStack(entity)
        return self.histories[entity]
    
    def record_event(
        self,
        event_type: EventType,
        actor: str,
        target: str,
        context: str,
        timestamp: int,
        witnesses: list[str] = None,
    ) -> dict:
        """
        Record a social event and propagate consequences.
        Returns vendetta information if triggered.
        """
        # Calculate relationship delta based on event type
        deltas = {
            EventType.HELPED: 15,
            EventType.SAVED: 30,
            EventType.KEPT_PROMISE: 20,
            EventType.COMPLIMENTED: 5,
            EventType.PROTECTED: 25,
            EventType.BETRAYED: -40,
            EventType.STOLE_FROM: -20,
            EventType.LIED_TO: -15,
            EventType.INSULTED: -10,
            EventType.THREATENED: -25,
            EventType.KILLED: -100,
            EventType.BROKE_PROMISE: -30,
            EventType.BRIBED: -5,  # Slight negative, they know you're manipulative
        }
        
        delta = deltas.get(event_type, 0)
        
        # Record in target's history
        target_history = self.get_history(target)
        event = target_history.record_event(
            event_type=event_type,
            target=target,
            actor=actor,
            context=context,
            relationship_delta=delta,
            timestamp=timestamp,
            witnesses=witnesses,
        )
        
        # Check for vendetta triggers
        vendetta_info = None
        if event_type == EventType.KILLED:
            vendetta_info = self._propagate_vendetta(target, actor, context, timestamp)
        
        # Propagate knowledge to witnesses
        if witnesses:
            for witness in witnesses:
                witness_history = self.get_history(witness)
                witness_history.record_event(
                    event_type=EventType.WITNESSED,
                    target=target,
                    actor=actor,
                    context=f"Witnessed: {context}",
                    relationship_delta=0,
                    timestamp=timestamp,
                )
        
        return {
            "event": event,
            "vendetta": vendetta_info,
        }
    
    def _propagate_vendetta(
        self,
        victim: str,
        killer: str,
        context: str,
        timestamp: int,
    ) -> dict | None:
        """Propagate vendetta to victim's family/allies."""
        affected = []
        
        # Find family
        for other, link in self.get_relations(victim):
            if link.relation_type in [RelationType.FAMILY, RelationType.LOVER]:
                # Create vendetta record
                other_history = self.get_history(other)
                other_history.record_event(
                    event_type=EventType.KILLED,
                    target=victim,
                    actor=killer,
                    context=f"Killed my {link.relation_type.value}: {context}",
                    relationship_delta=-100,
                    timestamp=timestamp,
                )
                affected.append({
                    "entity": other,
                    "relation": link.relation_type.value,
                    "narrative": f"{other} has sworn vendetta for {victim}'s death",
                })
        
        if affected:
            return {
                "victim": victim,
                "killer": killer,
                "vendettas": affected,
            }
        return None
    
    def get_narrator_context(self, for_entity: str) -> str:
        """Generate context about vendettas and grudges."""
        history = self.get_history(for_entity)
        
        # Check for active vendettas
        vendettas = []
        for event in history.events:
            if event.event_type == EventType.KILLED and event.relationship_delta < 0:
                vendettas.append(event)
        
        if not vendettas:
            return ""
        
        lines = ["[ACTIVE VENDETTAS]"]
        for v in vendettas[:3]:
            lines.append(f"• Against {v.actor}: {v.context}")
        
        return "\n".join(lines)


# ============================================================================
# Memory Fallibility System
# ============================================================================

class MemoryFallibility:
    """
    Models unreliable memory - beliefs degrade and mutate over time.
    Creates "unreliable narrators" for interrogation gameplay.
    """
    
    @staticmethod
    def decay_memory(
        original: str,
        time_elapsed: int,
        decay_rate: float = 0.1,
    ) -> str:
        """Degrade a memory over time."""
        # Calculate how much is forgotten
        decay = min(0.8, time_elapsed * decay_rate)
        
        if decay < 0.2:
            return original  # Still fresh
        elif decay < 0.4:
            return f"(vaguely) {original}"
        elif decay < 0.6:
            return f"(hazily) Something about... {original[:30]}..."
        else:
            return "(barely remembers) Something... can't quite recall..."
    
    @staticmethod
    def mutate_memory(
        original: str,
        bias: str = "neutral",
        mutation_chance: float = 0.3,
    ) -> str:
        """Mutate a memory based on bias."""
        if random.random() > mutation_chance:
            return original
        
        mutations = {
            "xenophobic": [
                ("a person", "a non-human"),
                ("someone", "one of *them*"),
                ("they", "those people"),
            ],
            "paranoid": [
                ("accident", "deliberate attack"),
                ("coincidence", "conspiracy"),
                ("mistake", "sabotage"),
            ],
            "optimistic": [
                ("attacked", "defended themselves"),
                ("stole", "borrowed"),
                ("threatened", "warned"),
            ],
            "pessimistic": [
                ("helped", "had ulterior motives"),
                ("gift", "bribe"),
                ("friend", "so-called 'friend'"),
            ],
        }
        
        bias_mutations = mutations.get(bias, [])
        result = original
        for old, new in bias_mutations[:1]:
            if old in result.lower():
                result = result.replace(old, new)
                break
        
        return result
    
    @staticmethod
    def get_unreliable_testimony(
        event: HistoryElement,
        witness_bias: str = "neutral",
        time_since: int = 0,
    ) -> str:
        """Generate an unreliable witness account."""
        base = event.context
        
        # Apply decay
        decayed = MemoryFallibility.decay_memory(base, time_since)
        
        # Apply mutation
        mutated = MemoryFallibility.mutate_memory(decayed, witness_bias)
        
        return mutated


# ============================================================================
# Information Propagation
# ============================================================================

class InformationPropagator:
    """
    Knowledge travels via social links over time.
    Simulates rumor mill and news spreading.
    """
    
    def __init__(self, social_graph: SocialGraph):
        self.graph = social_graph
        self.knowledge_map: dict[str, set[str]] = {}  # entity -> known event IDs
        self.rumors: list[dict] = []
    
    def propagate(self, event_id: str, origin: str, current_time: int) -> list[str]:
        """
        Propagate knowledge of an event through social network.
        Returns list of entities who now know about it.
        """
        newly_informed = []
        
        # Origin knows about it
        if origin not in self.knowledge_map:
            self.knowledge_map[origin] = set()
        self.knowledge_map[origin].add(event_id)
        
        # Spread to connected entities
        for other, link in self.graph.get_relations(origin):
            # Chance based on relationship strength and type
            spread_chance = link.strength * 0.5
            if link.relation_type == RelationType.FAMILY:
                spread_chance = 0.9
            elif link.relation_type == RelationType.FRIEND:
                spread_chance = 0.7
            
            if random.random() < spread_chance:
                if other not in self.knowledge_map:
                    self.knowledge_map[other] = set()
                if event_id not in self.knowledge_map[other]:
                    self.knowledge_map[other].add(event_id)
                    newly_informed.append(other)
        
        return newly_informed
    
    def who_knows(self, event_id: str) -> list[str]:
        """Get list of entities who know about an event."""
        return [e for e, known in self.knowledge_map.items() if event_id in known]


# ============================================================================
# Response Curves for Utility AI
# ============================================================================

class ResponseCurve:
    """
    Mathematical response curves for nuanced utility scoring.
    Transforms raw input (0-1) to output (0-1) with different shapes.
    """
    
    @staticmethod
    def linear(x: float) -> float:
        """Linear response: output = input."""
        return max(0, min(1, x))
    
    @staticmethod
    def quadratic(x: float) -> float:
        """Quadratic: slow start, fast finish."""
        return max(0, min(1, x * x))
    
    @staticmethod
    def inverse_quadratic(x: float) -> float:
        """Inverse quadratic: fast start, slow finish."""
        return max(0, min(1, 1 - (1 - x) ** 2))
    
    @staticmethod
    def logistic(x: float, steepness: float = 10.0, midpoint: float = 0.5) -> float:
        """
        S-curve: threshold behavior.
        Low values stay low, high values stay high, transition in middle.
        Perfect for bribe thresholds.
        """
        return 1 / (1 + math.exp(-steepness * (x - midpoint)))
    
    @staticmethod
    def step(x: float, threshold: float = 0.5) -> float:
        """Binary step: below threshold = 0, above = 1."""
        return 1.0 if x >= threshold else 0.0
    
    @staticmethod
    def bell(x: float, center: float = 0.5, width: float = 0.2) -> float:
        """Bell curve: peaks at center, falls off on sides."""
        return math.exp(-((x - center) ** 2) / (2 * width ** 2))


@dataclass
class UtilityConsideration:
    """A single consideration with response curve."""
    name: str
    curve_type: str = "linear"
    curve_params: dict = field(default_factory=dict)
    weight: float = 1.0
    
    def evaluate(self, raw_value: float) -> float:
        """Evaluate this consideration."""
        curves = {
            "linear": ResponseCurve.linear,
            "quadratic": ResponseCurve.quadratic,
            "inverse_quadratic": ResponseCurve.inverse_quadratic,
            "logistic": lambda x: ResponseCurve.logistic(x, **self.curve_params),
            "step": lambda x: ResponseCurve.step(x, **self.curve_params),
            "bell": lambda x: ResponseCurve.bell(x, **self.curve_params),
        }
        
        curve_fn = curves.get(self.curve_type, ResponseCurve.linear)
        return curve_fn(raw_value) * self.weight


# ============================================================================
# Convenience Functions
# ============================================================================

def create_social_graph() -> SocialGraph:
    """Create a new social graph."""
    return SocialGraph()


def quick_vendetta_check(
    graph: SocialGraph,
    victim: str,
    killer: str,
) -> list[str]:
    """Quick check for who has vendettas against killer."""
    family = graph.get_family(victim)
    return [f for f in family if f != killer]
