"""
Advanced World Simulation Systems - Deep World State and Dynamics

This module provides sophisticated world simulation systems for
creating living, breathing game worlds with persistent consequences.

Key Systems:
1. Relationship Dynamics - NPC-to-NPC and NPC-to-Player relationships
2. Flashback/Memory System - Trigger meaningful flashbacks
3. Consequence Propagation - Actions ripple through the world
4. Time & Calendar System - Track in-game time with events
5. Dialogue Memory - Remember and reference past conversations
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Any
import random
from collections import defaultdict


# =============================================================================
# RELATIONSHIP DYNAMICS SYSTEM
# =============================================================================

class RelationshipType(Enum):
    """Types of relationships between entities."""
    FAMILY = "family"              # Blood/adopted relations
    ROMANTIC = "romantic"          # Love interests
    FRIENDSHIP = "friendship"      # Platonic bonds
    PROFESSIONAL = "professional"  # Work/mission related
    RIVALRY = "rivalry"            # Competitive opposition
    ENEMY = "enemy"                # Active hostility
    MENTOR = "mentor"              # Teacher/student
    DEBT = "debt"                  # Owes something


class RelationshipDimension(Enum):
    """Dimensions of relationship quality."""
    TRUST = "trust"           # Do they believe each other?
    RESPECT = "respect"       # Do they value each other?
    AFFECTION = "affection"   # Do they like each other?
    FEAR = "fear"             # Are they afraid of each other?
    OBLIGATION = "obligation" # Do they owe each other?


@dataclass
class Relationship:
    """A relationship between two entities."""
    entity_a: str
    entity_b: str
    relationship_type: RelationshipType
    dimensions: Dict[RelationshipDimension, float] = field(default_factory=dict)  # -1.0 to 1.0
    history: List[Dict[str, str]] = field(default_factory=list)  # Key moments
    secrets_known: List[str] = field(default_factory=list)  # What A knows about B
    shared_experiences: List[str] = field(default_factory=list)
    
    def get_overall_quality(self) -> float:
        """Calculate overall relationship quality."""
        if not self.dimensions:
            return 0.0
        
        # Weight dimensions differently
        weights = {
            RelationshipDimension.TRUST: 0.3,
            RelationshipDimension.RESPECT: 0.25,
            RelationshipDimension.AFFECTION: 0.25,
            RelationshipDimension.FEAR: -0.1,  # Fear is usually negative
            RelationshipDimension.OBLIGATION: 0.1
        }
        
        total = 0.0
        for dim, value in self.dimensions.items():
            total += value * weights.get(dim, 0.2)
        
        return max(-1.0, min(1.0, total))


@dataclass
class RelationshipDynamicsSystem:
    """
    Tracks complex relationships between NPCs and players.
    
    Enables relationship arcs, betrayals, alliances,
    and meaningful social consequences.
    """
    
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    relationship_events: List[Dict[str, Any]] = field(default_factory=list)
    
    def _get_key(self, entity_a: str, entity_b: str) -> str:
        """Get consistent key for relationship pair."""
        return f"{min(entity_a, entity_b)}:{max(entity_a, entity_b)}"
    
    def create_relationship(self, entity_a: str, entity_b: str,
                             rel_type: RelationshipType,
                             initial_dimensions: Dict[RelationshipDimension, float] = None):
        """Create a new relationship."""
        key = self._get_key(entity_a, entity_b)
        
        dims = initial_dimensions or {
            RelationshipDimension.TRUST: 0.0,
            RelationshipDimension.RESPECT: 0.0,
            RelationshipDimension.AFFECTION: 0.0
        }
        
        self.relationships[key] = Relationship(
            entity_a=entity_a,
            entity_b=entity_b,
            relationship_type=rel_type,
            dimensions=dims
        )
    
    def modify_dimension(self, entity_a: str, entity_b: str,
                          dimension: RelationshipDimension,
                          change: float, reason: str = ""):
        """Modify a relationship dimension."""
        key = self._get_key(entity_a, entity_b)
        
        if key in self.relationships:
            rel = self.relationships[key]
            old_value = rel.dimensions.get(dimension, 0.0)
            new_value = max(-1.0, min(1.0, old_value + change))
            rel.dimensions[dimension] = new_value
            
            if abs(change) >= 0.2:  # Significant change
                rel.history.append({
                    "dimension": dimension.value,
                    "change": f"{old_value:.2f} → {new_value:.2f}",
                    "reason": reason
                })
    
    def add_shared_experience(self, entity_a: str, entity_b: str, experience: str):
        """Add a shared experience to relationship."""
        key = self._get_key(entity_a, entity_b)
        if key in self.relationships:
            self.relationships[key].shared_experiences.append(experience)
    
    def get_relationship(self, entity_a: str, entity_b: str) -> Optional[Relationship]:
        """Get relationship between two entities."""
        key = self._get_key(entity_a, entity_b)
        return self.relationships.get(key)
    
    def get_relationship_guidance(self, active_npcs: List[str], 
                                    player_name: str = "player") -> str:
        """Generate relationship context for narrator."""
        if not active_npcs:
            return ""
        
        rel_summaries = []
        
        for npc in active_npcs:
            # Player-NPC relationship
            rel = self.get_relationship(player_name, npc)
            if rel:
                quality = rel.get_overall_quality()
                quality_label = "hostile" if quality < -0.3 else \
                               "tense" if quality < 0 else \
                               "neutral" if quality < 0.3 else \
                               "warm" if quality < 0.6 else "close"
                
                dim_text = ", ".join([f"{d.value}:{v:.1f}" for d, v in rel.dimensions.items()])
                
                shared = rel.shared_experiences[-2:] if rel.shared_experiences else []
                shared_text = f" | Shared: {'; '.join(shared)}" if shared else ""
                
                rel_summaries.append(f"  {npc} ({quality_label}): {dim_text}{shared_text}")
        
        # NPC-NPC relationships
        npc_rels = []
        for i, npc1 in enumerate(active_npcs):
            for npc2 in active_npcs[i+1:]:
                rel = self.get_relationship(npc1, npc2)
                if rel:
                    quality = rel.get_overall_quality()
                    if abs(quality) > 0.3:  # Only notable relationships
                        label = "allies" if quality > 0.3 else "hostile"
                        npc_rels.append(f"  {npc1} ↔ {npc2}: {label}")
        
        if not rel_summaries and not npc_rels:
            return ""
        
        return f"""<relationships>
PLAYER RELATIONSHIPS:
{chr(10).join(rel_summaries) if rel_summaries else "  No established relationships"}

NPC DYNAMICS:
{chr(10).join(npc_rels) if npc_rels else "  No notable NPC relationships"}

RELATIONSHIP GUIDANCE:
  - Reference shared experiences naturally
  - Trust level affects what NPCs reveal
  - Respect affects how they respond to commands
  - History should inform present interactions
</relationships>"""
    
    def to_dict(self) -> dict:
        return {
            "relationships": {
                k: {
                    "entity_a": r.entity_a,
                    "entity_b": r.entity_b,
                    "relationship_type": r.relationship_type.value,
                    "dimensions": {d.value: v for d, v in r.dimensions.items()},
                    "history": r.history[-10:],
                    "secrets_known": r.secrets_known,
                    "shared_experiences": r.shared_experiences[-10:]
                } for k, r in self.relationships.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RelationshipDynamicsSystem":
        system = cls()
        for k, r in data.get("relationships", {}).items():
            system.relationships[k] = Relationship(
                entity_a=r["entity_a"],
                entity_b=r["entity_b"],
                relationship_type=RelationshipType(r["relationship_type"]),
                dimensions={RelationshipDimension(d): v for d, v in r.get("dimensions", {}).items()},
                history=r.get("history", []),
                secrets_known=r.get("secrets_known", []),
                shared_experiences=r.get("shared_experiences", [])
            )
        return system


# =============================================================================
# FLASHBACK/MEMORY SYSTEM
# =============================================================================

class FlashbackTrigger(Enum):
    """What can trigger a flashback."""
    LOCATION = "location"        # Being in a significant place
    OBJECT = "object"            # Seeing a significant object
    PERSON = "person"            # Meeting someone from the past
    PHRASE = "phrase"            # Hearing specific words
    SENSORY = "sensory"          # Smell, sound, taste
    EMOTIONAL = "emotional"      # Reaching emotional threshold
    ANNIVERSARY = "anniversary"  # Time-based trigger


@dataclass
class MemoryFragment:
    """A memory that can be triggered."""
    memory_id: str
    description: str
    emotional_weight: float  # 0.0 to 1.0 (how impactful)
    trigger_type: FlashbackTrigger
    trigger_conditions: Dict[str, str]  # What triggers it
    characters_involved: List[str]
    has_been_triggered: bool = False
    times_triggered: int = 0


@dataclass
class FlashbackSystem:
    """
    Triggers meaningful flashbacks at emotionally resonant moments.
    
    Creates connections between past and present,
    reveals character depth, and provides context.
    """
    
    memories: Dict[str, MemoryFragment] = field(default_factory=dict)
    recent_triggers: List[str] = field(default_factory=list)
    current_scene: int = 0
    
    # Flashback presentation techniques
    PRESENTATION_TECHNIQUES: List[str] = field(default_factory=lambda: [
        "Sensory transition: Same sense in present triggers memory",
        "Mid-sentence cut: Present dialogue interrupted by past",
        "Parallel action: What they're doing mirrors what they did",
        "Object focus: Camera lingers on object, world shifts",
        "Sound bridge: Sound from past bleeds into present"
    ])
    
    def register_memory(self, memory_id: str, description: str,
                         weight: float, trigger: FlashbackTrigger,
                         conditions: Dict[str, str],
                         characters: List[str] = None) -> MemoryFragment:
        """Register a memory for potential flashback."""
        memory = MemoryFragment(
            memory_id=memory_id,
            description=description,
            emotional_weight=weight,
            trigger_type=trigger,
            trigger_conditions=conditions,
            characters_involved=characters or []
        )
        self.memories[memory_id] = memory
        return memory
    
    def check_triggers(self, current_context: Dict[str, str]) -> List[MemoryFragment]:
        """Check if current context triggers any memories."""
        triggered = []
        
        for memory in self.memories.values():
            if memory.memory_id in self.recent_triggers[-3:]:
                continue  # Don't repeat too soon
            
            # Check if conditions match
            match = False
            for key, value in memory.trigger_conditions.items():
                if key in current_context:
                    if value.lower() in current_context[key].lower():
                        match = True
                        break
            
            if match:
                triggered.append(memory)
        
        return sorted(triggered, key=lambda m: m.emotional_weight, reverse=True)
    
    def trigger_memory(self, memory_id: str):
        """Mark a memory as triggered."""
        if memory_id in self.memories:
            self.memories[memory_id].has_been_triggered = True
            self.memories[memory_id].times_triggered += 1
            self.recent_triggers.append(memory_id)
    
    def get_flashback_guidance(self, triggered_memory: MemoryFragment = None) -> str:
        """Generate flashback guidance for narrator."""
        
        technique = random.choice(self.PRESENTATION_TECHNIQUES)
        
        if triggered_memory:
            return f"""<flashback_opportunity>
⭐ MEMORY TRIGGERED: "{triggered_memory.description}"
Emotional weight: {triggered_memory.emotional_weight:.0%}
Characters: {', '.join(triggered_memory.characters_involved) if triggered_memory.characters_involved else 'Solo'}

PRESENTATION: {technique}

FLASHBACK CRAFT:
  - Transition should feel inevitable, not arbitrary
  - Past tense in flashback, present tense return
  - Sensory details anchor the memory (what did it smell like?)
  - End flashback at emotionally resonant point
  - Return to present should echo or contrast the memory

THE MEMORY'S PURPOSE:
  What does this memory REVEAL about the character?
  What does it EXPLAIN about their present behavior?
  How does it CHANGE how we see them?
</flashback_opportunity>"""
        
        # No specific trigger - general guidance
        untriggered = [m for m in self.memories.values() if not m.has_been_triggered]
        
        if untriggered:
            upcoming = untriggered[0]
            return f"""<flashback_potential>
PENDING MEMORIES: {len(untriggered)} untriggered memories

NEXT IN QUEUE: "{upcoming.description}"
  Trigger: {upcoming.trigger_type.value} - {upcoming.trigger_conditions}
  Weight: {upcoming.emotional_weight:.0%}

Consider introducing trigger condition naturally when:
  - Emotional intensity warrants deeper context
  - Character reaches decision point
  - Present echoes past in meaningful way
</flashback_potential>"""
        
        return ""
    
    def to_dict(self) -> dict:
        return {
            "memories": {
                mid: {
                    "memory_id": m.memory_id,
                    "description": m.description,
                    "emotional_weight": m.emotional_weight,
                    "trigger_type": m.trigger_type.value,
                    "trigger_conditions": m.trigger_conditions,
                    "characters_involved": m.characters_involved,
                    "has_been_triggered": m.has_been_triggered,
                    "times_triggered": m.times_triggered
                } for mid, m in self.memories.items()
            },
            "recent_triggers": self.recent_triggers[-10:],
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FlashbackSystem":
        system = cls()
        system.recent_triggers = data.get("recent_triggers", [])
        system.current_scene = data.get("current_scene", 0)
        
        for mid, m in data.get("memories", {}).items():
            system.memories[mid] = MemoryFragment(
                memory_id=m["memory_id"],
                description=m["description"],
                emotional_weight=m["emotional_weight"],
                trigger_type=FlashbackTrigger(m["trigger_type"]),
                trigger_conditions=m["trigger_conditions"],
                characters_involved=m.get("characters_involved", []),
                has_been_triggered=m.get("has_been_triggered", False),
                times_triggered=m.get("times_triggered", 0)
            )
        return system


# =============================================================================
# CONSEQUENCE PROPAGATION SYSTEM
# =============================================================================

class ConsequenceScope(Enum):
    """How far a consequence spreads."""
    IMMEDIATE = "immediate"    # Right now, here
    LOCAL = "local"            # This area/group
    REGIONAL = "regional"      # Wider area
    GLOBAL = "global"          # Everywhere
    PERSONAL = "personal"      # Affects specific person


class ConsequenceType(Enum):
    """Types of consequences."""
    REPUTATION = "reputation"    # How others see you
    RESOURCE = "resource"        # Gain/loss of resources
    RELATIONSHIP = "relationship" # Bond changes
    OPPORTUNITY = "opportunity"  # Doors open/close
    DANGER = "danger"            # New threats
    ALLY = "ally"                # New friends/enemies
    KNOWLEDGE = "knowledge"      # Information spreads


@dataclass
class Consequence:
    """A consequence of player action."""
    consequence_id: str
    source_action: str
    consequence_type: ConsequenceType
    scope: ConsequenceScope
    description: str
    delay_scenes: int  # How long before it manifests
    scenes_until_manifest: int
    has_manifested: bool = False
    manifest_description: str = ""


@dataclass
class ConsequencePropagationSystem:
    """
    Tracks how actions ripple through the world over time.
    
    Ensures player actions have lasting effects and
    the world feels responsive to their choices.
    """
    
    pending_consequences: List[Consequence] = field(default_factory=list)
    manifested_consequences: List[Consequence] = field(default_factory=list)
    current_scene: int = 0
    
    # Consequence manifestation patterns
    MANIFESTATION_PATTERNS: Dict[ConsequenceType, List[str]] = field(default_factory=lambda: {
        ConsequenceType.REPUTATION: [
            "NPCs treat them differently based on reputation",
            "Rumors have spread—they're recognized",
            "Doors open (or close) based on what's known about them"
        ],
        ConsequenceType.RESOURCE: [
            "The gain/loss becomes apparent",
            "What they spent/saved matters now",
            "Resource scarcity or abundance creates new problems/opportunities"
        ],
        ConsequenceType.RELATIONSHIP: [
            "Someone who heard what they did reaches out",
            "Past kindness/cruelty returns through proxy",
            "The relationship change affects a third party"
        ],
        ConsequenceType.DANGER: [
            "The threat they created/avoided catches up",
            "Someone they wronged has been planning",
            "The danger has evolved while they were busy"
        ],
        ConsequenceType.OPPORTUNITY: [
            "A door opens because of past action",
            "What they did qualified them for this",
            "Their reputation preceded them—favorably"
        ]
    })
    
    def queue_consequence(self, source_action: str, cons_type: ConsequenceType,
                           scope: ConsequenceScope, description: str,
                           delay: int = 3) -> Consequence:
        """Queue a consequence for future manifestation."""
        cons = Consequence(
            consequence_id=f"cons_{len(self.pending_consequences)}_{self.current_scene}",
            source_action=source_action,
            consequence_type=cons_type,
            scope=scope,
            description=description,
            delay_scenes=delay,
            scenes_until_manifest=delay
        )
        self.pending_consequences.append(cons)
        return cons
    
    def advance_scene(self):
        """Advance time and check for manifesting consequences."""
        self.current_scene += 1
        
        newly_manifested = []
        still_pending = []
        
        for cons in self.pending_consequences:
            cons.scenes_until_manifest -= 1
            if cons.scenes_until_manifest <= 0:
                cons.has_manifested = True
                newly_manifested.append(cons)
                self.manifested_consequences.append(cons)
            else:
                still_pending.append(cons)
        
        self.pending_consequences = still_pending
        return newly_manifested
    
    def get_ready_consequences(self) -> List[Consequence]:
        """Get consequences ready to manifest this scene."""
        return [c for c in self.pending_consequences if c.scenes_until_manifest <= 1]
    
    def get_consequence_guidance(self) -> str:
        """Generate consequence propagation guidance."""
        ready = self.get_ready_consequences()
        
        ready_text = ""
        if ready:
            ready_items = []
            for c in ready[:3]:
                patterns = self.MANIFESTATION_PATTERNS.get(c.consequence_type, [])
                pattern = random.choice(patterns) if patterns else "Natural consequence"
                ready_items.append(f"""  [{c.consequence_type.value}] (from: "{c.source_action[:40]}...")
    Effect: {c.description}
    Pattern: {pattern}""")
            
            ready_text = f"""⚠️ CONSEQUENCES MANIFESTING:

{chr(10).join(ready_items)}"""
        
        pending_summary = ""
        if self.pending_consequences:
            by_delay = defaultdict(list)
            for c in self.pending_consequences:
                by_delay[c.scenes_until_manifest].append(c.consequence_type.value)
            
            pending_items = [f"  {delay} scenes: {', '.join(types)}" 
                            for delay, types in sorted(by_delay.items())]
            pending_summary = f"""
PENDING ({len(self.pending_consequences)} total):
{chr(10).join(pending_items[:5])}"""
        
        return f"""<consequence_propagation>
{ready_text if ready_text else "No consequences ready to manifest."}
{pending_summary}

THE RIPPLE PRINCIPLE:
  - Every significant action creates waves
  - Waves reach different shores at different times
  - The player should sometimes be surprised by what returns to them
  - But it should always feel earned, not arbitrary

MANIFESTATION CRAFT:
  - Callback to the original action (remind them what they did)
  - Show the chain of causation (how did this get from there to here?)
  - Make the consequence feel proportional (match action weight)
  - Leave room for response (consequence creates new choice)
</consequence_propagation>"""
    
    def to_dict(self) -> dict:
        return {
            "pending_consequences": [
                {
                    "consequence_id": c.consequence_id,
                    "source_action": c.source_action,
                    "consequence_type": c.consequence_type.value,
                    "scope": c.scope.value,
                    "description": c.description,
                    "delay_scenes": c.delay_scenes,
                    "scenes_until_manifest": c.scenes_until_manifest,
                    "has_manifested": c.has_manifested
                } for c in self.pending_consequences
            ],
            "manifested_consequences": [
                {
                    "consequence_id": c.consequence_id,
                    "source_action": c.source_action,
                    "description": c.description
                } for c in self.manifested_consequences[-20:]
            ],
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ConsequencePropagationSystem":
        system = cls()
        system.current_scene = data.get("current_scene", 0)
        
        for c in data.get("pending_consequences", []):
            system.pending_consequences.append(Consequence(
                consequence_id=c["consequence_id"],
                source_action=c["source_action"],
                consequence_type=ConsequenceType(c["consequence_type"]),
                scope=ConsequenceScope(c["scope"]),
                description=c["description"],
                delay_scenes=c["delay_scenes"],
                scenes_until_manifest=c["scenes_until_manifest"],
                has_manifested=c.get("has_manifested", False)
            ))
        return system


# =============================================================================
# TIME & CALENDAR SYSTEM
# =============================================================================

class TimeOfDay(Enum):
    """Periods of the day."""
    DAWN = "dawn"
    MORNING = "morning"
    MIDDAY = "midday"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    EVENING = "evening"
    NIGHT = "night"
    LATE_NIGHT = "late_night"


@dataclass
class ScheduledEvent:
    """An event scheduled to occur."""
    event_id: str
    description: str
    trigger_day: int
    trigger_time: TimeOfDay
    is_recurring: bool = False
    recurrence_days: int = 0
    has_occurred: bool = False
    importance: float = 0.5  # 0.0 to 1.0


@dataclass
class TimeCalendarSystem:
    """
    Tracks in-game time with events and deadlines.
    
    Creates temporal pressure, enables scheduling,
    and makes the world feel like it has rhythms.
    """
    
    current_day: int = 1
    current_time: TimeOfDay = TimeOfDay.MORNING
    scheduled_events: List[ScheduledEvent] = field(default_factory=list)
    deadlines: Dict[str, int] = field(default_factory=dict)  # name: day
    
    # Time atmosphere by period
    TIME_ATMOSPHERE: Dict[TimeOfDay, Dict[str, str]] = field(default_factory=lambda: {
        TimeOfDay.DAWN: {
            "light": "First light bleeding through, colors muted",
            "activity": "World stirring, early risers, promise or dread",
            "mood": "Potential, beginning, hope or exhaustion"
        },
        TimeOfDay.MORNING: {
            "light": "Bright, harsh, revealing",
            "activity": "Full activity, business, purpose",
            "mood": "Energy, productivity, mundane reality"
        },
        TimeOfDay.MIDDAY: {
            "light": "Direct, shadowless, unforgiving",
            "activity": "Peak activity, exposed, no hiding",
            "mood": "Clarity, exposure, nowhere to hide"
        },
        TimeOfDay.DUSK: {
            "light": "Golden hour, lengthening shadows",
            "activity": "Winding down, transitions, liminality",
            "mood": "Melancholy, reflection, change coming"
        },
        TimeOfDay.NIGHT: {
            "light": "Artificial pools in darkness, sharp contrasts",
            "activity": "Different world, different rules, different people",
            "mood": "Danger, intimacy, secrets, vulnerability"
        },
        TimeOfDay.LATE_NIGHT: {
            "light": "Deep darkness, exhaustion, the small hours",
            "activity": "Only the desperate, the determined, the lonely",
            "mood": "Isolation, truth-telling, the walls come down"
        }
    })
    
    TIME_ORDER: List[TimeOfDay] = field(default_factory=lambda: [
        TimeOfDay.DAWN, TimeOfDay.MORNING, TimeOfDay.MIDDAY,
        TimeOfDay.AFTERNOON, TimeOfDay.DUSK, TimeOfDay.EVENING,
        TimeOfDay.NIGHT, TimeOfDay.LATE_NIGHT
    ])
    
    def advance_time(self, periods: int = 1):
        """Advance time by a number of periods."""
        current_idx = self.TIME_ORDER.index(self.current_time)
        new_idx = (current_idx + periods) % len(self.TIME_ORDER)
        
        # Check if we crossed midnight
        days_passed = (current_idx + periods) // len(self.TIME_ORDER)
        
        self.current_time = self.TIME_ORDER[new_idx]
        self.current_day += days_passed
    
    def schedule_event(self, event_id: str, description: str,
                        day: int, time: TimeOfDay,
                        importance: float = 0.5) -> ScheduledEvent:
        """Schedule an event."""
        event = ScheduledEvent(
            event_id=event_id,
            description=description,
            trigger_day=day,
            trigger_time=time,
            importance=importance
        )
        self.scheduled_events.append(event)
        return event
    
    def set_deadline(self, name: str, days_until: int):
        """Set a deadline."""
        self.deadlines[name] = self.current_day + days_until
    
    def get_imminent_events(self) -> List[ScheduledEvent]:
        """Get events happening now or very soon."""
        imminent = []
        for event in self.scheduled_events:
            if event.has_occurred:
                continue
            if event.trigger_day == self.current_day and event.trigger_time == self.current_time:
                imminent.append(event)
            elif event.trigger_day == self.current_day:
                # Same day
                current_idx = self.TIME_ORDER.index(self.current_time)
                event_idx = self.TIME_ORDER.index(event.trigger_time)
                if 0 < event_idx - current_idx <= 2:  # Coming up soon
                    imminent.append(event)
        
        return sorted(imminent, key=lambda e: e.importance, reverse=True)
    
    def get_time_guidance(self) -> str:
        """Generate time and calendar guidance."""
        atmosphere = self.TIME_ATMOSPHERE.get(self.current_time, {})
        
        atmo_text = "\n".join([f"  {k}: {v}" for k, v in atmosphere.items()])
        
        # Imminent events
        imminent = self.get_imminent_events()
        events_text = ""
        if imminent:
            events_items = [f"  - {e.description} ({e.trigger_time.value})" for e in imminent[:3]]
            events_text = f"""
IMMINENT EVENTS:
{chr(10).join(events_items)}"""
        
        # Deadlines
        deadline_text = ""
        urgent = [(name, day - self.current_day) for name, day in self.deadlines.items() 
                  if day - self.current_day <= 3 and day >= self.current_day]
        if urgent:
            deadline_items = [f"  - {name}: {days} days" for name, days in sorted(urgent, key=lambda x: x[1])]
            deadline_text = f"""
⏰ DEADLINES:
{chr(10).join(deadline_items)}"""
        
        return f"""<time_calendar>
DAY {self.current_day} | {self.current_time.value.upper()}

ATMOSPHERE:
{atmo_text}
{events_text}{deadline_text}

TIME AS NARRATIVE TOOL:
  - Time of day affects mood, available NPCs, possible actions
  - Deadlines create urgency without railroad
  - The passage of time should be felt (fatigue, change, decay)
  - Different hours attract different people, different dangers
</time_calendar>"""
    
    def to_dict(self) -> dict:
        return {
            "current_day": self.current_day,
            "current_time": self.current_time.value,
            "scheduled_events": [
                {
                    "event_id": e.event_id,
                    "description": e.description,
                    "trigger_day": e.trigger_day,
                    "trigger_time": e.trigger_time.value,
                    "importance": e.importance,
                    "has_occurred": e.has_occurred
                } for e in self.scheduled_events if not e.has_occurred
            ],
            "deadlines": self.deadlines
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TimeCalendarSystem":
        system = cls()
        system.current_day = data.get("current_day", 1)
        system.current_time = TimeOfDay(data.get("current_time", "morning"))
        system.deadlines = data.get("deadlines", {})
        
        for e in data.get("scheduled_events", []):
            system.scheduled_events.append(ScheduledEvent(
                event_id=e["event_id"],
                description=e["description"],
                trigger_day=e["trigger_day"],
                trigger_time=TimeOfDay(e["trigger_time"]),
                importance=e.get("importance", 0.5),
                has_occurred=e.get("has_occurred", False)
            ))
        return system


# =============================================================================
# DIALOGUE MEMORY SYSTEM
# =============================================================================

@dataclass
class DialogueMemory:
    """A remembered piece of dialogue."""
    speaker: str
    listener: str
    content: str
    scene: int
    emotional_context: str
    is_lie: bool = False
    is_promise: bool = False
    is_secret: bool = False
    has_been_referenced: bool = False


@dataclass
class DialogueMemorySystem:
    """
    Remembers and references past conversations.
    
    Enables callbacks to previous dialogue, catching
    characters in lies, and fulfilling/breaking promises.
    """
    
    memories: List[DialogueMemory] = field(default_factory=list)
    current_scene: int = 0
    
    def record_dialogue(self, speaker: str, listener: str, content: str,
                         emotional_context: str = "",
                         is_lie: bool = False, is_promise: bool = False,
                         is_secret: bool = False):
        """Record a piece of dialogue."""
        memory = DialogueMemory(
            speaker=speaker,
            listener=listener,
            content=content,
            scene=self.current_scene,
            emotional_context=emotional_context,
            is_lie=is_lie,
            is_promise=is_promise,
            is_secret=is_secret
        )
        self.memories.append(memory)
    
    def get_memories_with(self, character: str) -> List[DialogueMemory]:
        """Get all dialogue memories involving a character."""
        return [m for m in self.memories 
                if m.speaker == character or m.listener == character]
    
    def get_unfulfilled_promises(self) -> List[DialogueMemory]:
        """Get promises that haven't been addressed."""
        return [m for m in self.memories 
                if m.is_promise and not m.has_been_referenced]
    
    def get_catchable_lies(self, present_character: str) -> List[DialogueMemory]:
        """Get lies that could be exposed with the present character."""
        return [m for m in self.memories 
                if m.is_lie and not m.has_been_referenced
                and present_character in [m.speaker, m.listener]]
    
    def get_dialogue_guidance(self, active_npcs: List[str]) -> str:
        """Generate dialogue memory guidance."""
        callbacks = []
        
        for npc in active_npcs:
            npc_memories = self.get_memories_with(npc)[-5:]
            if npc_memories:
                recent = npc_memories[-1]
                callbacks.append(f"  {npc}: \"{recent.content[:50]}...\" (scene {recent.scene})")
        
        # Promises
        promises = self.get_unfulfilled_promises()[:2]
        promises_text = ""
        if promises:
            promise_items = [f"  - {p.speaker} promised: \"{p.content[:40]}...\"" for p in promises]
            promises_text = f"""
UNFULFILLED PROMISES:
{chr(10).join(promise_items)}"""
        
        # Lies
        lies_text = ""
        for npc in active_npcs:
            lies = self.get_catchable_lies(npc)
            if lies:
                lie = lies[0]
                lies_text = f"""
🎭 CATCHABLE LIE:
  {lie.speaker} told {lie.listener}: \"{lie.content[:40]}...\"
  This could be exposed now."""
                break
        
        callback_text = "\n".join(callbacks) if callbacks else "  No recorded dialogue with present NPCs"
        
        return f"""<dialogue_memory>
RECENT DIALOGUE WITH PRESENT NPCS:
{callback_text}
{promises_text}{lies_text}

DIALOGUE CALLBACK TECHNIQUES:
  - "You said X, but now Y" — catch inconsistency
  - "Remember when you told me..." — emotional callback
  - "You promised" — obligation reminder
  - Echo their words back at a crucial moment

VERISIMILITUDE:
  Characters should remember what was said to them.
  Lies should be catchable. Promises should matter.
</dialogue_memory>"""
    
    def to_dict(self) -> dict:
        return {
            "memories": [
                {
                    "speaker": m.speaker,
                    "listener": m.listener,
                    "content": m.content,
                    "scene": m.scene,
                    "emotional_context": m.emotional_context,
                    "is_lie": m.is_lie,
                    "is_promise": m.is_promise,
                    "is_secret": m.is_secret,
                    "has_been_referenced": m.has_been_referenced
                } for m in self.memories[-50:]  # Keep last 50
            ],
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DialogueMemorySystem":
        system = cls()
        system.current_scene = data.get("current_scene", 0)
        
        for m in data.get("memories", []):
            system.memories.append(DialogueMemory(
                speaker=m["speaker"],
                listener=m["listener"],
                content=m["content"],
                scene=m["scene"],
                emotional_context=m.get("emotional_context", ""),
                is_lie=m.get("is_lie", False),
                is_promise=m.get("is_promise", False),
                is_secret=m.get("is_secret", False),
                has_been_referenced=m.get("has_been_referenced", False)
            ))
        return system


# =============================================================================
# MASTER ADVANCED SIMULATION ENGINE
# =============================================================================

@dataclass
class AdvancedSimulationEngine:
    """Master engine coordinating all advanced simulation systems."""
    
    relationships: RelationshipDynamicsSystem = field(default_factory=RelationshipDynamicsSystem)
    flashbacks: FlashbackSystem = field(default_factory=FlashbackSystem)
    consequences: ConsequencePropagationSystem = field(default_factory=ConsequencePropagationSystem)
    time: TimeCalendarSystem = field(default_factory=TimeCalendarSystem)
    dialogue: DialogueMemorySystem = field(default_factory=DialogueMemorySystem)
    
    def get_comprehensive_guidance(
        self,
        active_npcs: List[str] = None,
        player_name: str = "player",
        current_context: Dict[str, str] = None
    ) -> str:
        """Generate comprehensive simulation guidance."""
        
        sections = []
        
        # Relationships
        rel_guidance = self.relationships.get_relationship_guidance(
            active_npcs or [], player_name
        )
        if rel_guidance:
            sections.append(rel_guidance)
        
        # Flashbacks
        if current_context:
            triggered = self.flashbacks.check_triggers(current_context)
            if triggered:
                sections.append(self.flashbacks.get_flashback_guidance(triggered[0]))
        
        # Consequences
        cons_guidance = self.consequences.get_consequence_guidance()
        if cons_guidance:
            sections.append(cons_guidance)
        
        # Time
        time_guidance = self.time.get_time_guidance()
        if time_guidance:
            sections.append(time_guidance)
        
        # Dialogue
        if active_npcs:
            dialogue_guidance = self.dialogue.get_dialogue_guidance(active_npcs)
            if dialogue_guidance:
                sections.append(dialogue_guidance)
        
        if not sections:
            return ""
        
        return f"""
<advanced_simulation>
=== WORLD SIMULATION GUIDANCE ===
{chr(10).join(sections)}
</advanced_simulation>
"""
    
    def advance_scene(self):
        """Advance all systems by one scene."""
        self.flashbacks.current_scene += 1
        self.consequences.advance_scene()
        self.dialogue.current_scene += 1
    
    def to_dict(self) -> dict:
        return {
            "relationships": self.relationships.to_dict(),
            "flashbacks": self.flashbacks.to_dict(),
            "consequences": self.consequences.to_dict(),
            "time": self.time.to_dict(),
            "dialogue": self.dialogue.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AdvancedSimulationEngine":
        engine = cls()
        if "relationships" in data:
            engine.relationships = RelationshipDynamicsSystem.from_dict(data["relationships"])
        if "flashbacks" in data:
            engine.flashbacks = FlashbackSystem.from_dict(data["flashbacks"])
        if "consequences" in data:
            engine.consequences = ConsequencePropagationSystem.from_dict(data["consequences"])
        if "time" in data:
            engine.time = TimeCalendarSystem.from_dict(data["time"])
        if "dialogue" in data:
            engine.dialogue = DialogueMemorySystem.from_dict(data["dialogue"])
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ADVANCED SIMULATION ENGINE - TEST")
    print("=" * 60)
    
    engine = AdvancedSimulationEngine()
    
    # Set up some relationships
    engine.relationships.create_relationship(
        "player", "Torres",
        RelationshipType.PROFESSIONAL,
        {RelationshipDimension.TRUST: 0.2, RelationshipDimension.RESPECT: 0.4}
    )
    engine.relationships.add_shared_experience("player", "Torres", "Survived the ambush together")
    
    # Set up a flashback trigger
    engine.flashbacks.register_memory(
        "family_loss",
        "The day they lost their family on Station Omega",
        weight=0.9,
        trigger=FlashbackTrigger.LOCATION,
        conditions={"location": "Station Omega"},
        characters=["Mother", "Sister"]
    )
    
    # Queue a consequence
    engine.consequences.queue_consequence(
        source_action="Spared the pirate captain",
        cons_type=ConsequenceType.ALLY,
        scope=ConsequenceScope.REGIONAL,
        description="Pirate captain sends warning about incoming danger",
        delay=3
    )
    
    # Set up time
    engine.time.schedule_event(
        "meeting", "Secret meeting with the informant",
        day=1, time=TimeOfDay.NIGHT,
        importance=0.8
    )
    engine.time.set_deadline("escape_window", days_until=5)
    
    # Record dialogue
    engine.dialogue.record_dialogue(
        "Torres", "player",
        "I'll cover you when we reach the cargo bay.",
        is_promise=True
    )
    
    print("\n--- COMPREHENSIVE GUIDANCE ---")
    guidance = engine.get_comprehensive_guidance(
        active_npcs=["Torres"],
        current_context={"location": "Docking Bay"}
    )
    print(guidance[:3000] + "..." if len(guidance) > 3000 else guidance)
