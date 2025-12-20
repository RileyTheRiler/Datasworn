"""
Living World Simulation System for Starforged AI Game Master.

Manages background events, NPC lifecycles, and faction developments.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import random
import time

# ============================================================================
# Enums
# ============================================================================

class EventType(Enum):
    """Types of world events."""
    FACTION_WAR = "faction_war"
    FACTION_PEACE = "faction_peace"
    FACTION_EXPANSION = "faction_expansion"
    FACTION_CONTRACTION = "faction_contraction"
    NPC_BIRTH = "npc_birth"
    NPC_DEATH = "npc_death"
    NPC_MOVE = "npc_move"
    DISCOVERY = "discovery"
    CRISIS = "crisis"


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class WorldEvent:
    """A significant event in the world."""
    id: str
    event_type: EventType
    description: str
    location: str
    related_factions: List[str] = field(default_factory=list)
    related_npcs: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "description": self.description,
            "location": self.location,
            "related_factions": self.related_factions,
            "related_npcs": self.related_npcs,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldEvent":
        return cls(
            id=data["id"],
            event_type=EventType(data["event_type"]),
            description=data["description"],
            location=data["location"],
            related_factions=data.get("related_factions", []),
            related_npcs=data.get("related_npcs", []),
            timestamp=data.get("timestamp", time.time())
        )


# ============================================================================
# Simulation Systems
# ============================================================================

class WorldSimulator:
    """Orchestrates background simulation events."""
    
    def __init__(self):
        self.events: List[WorldEvent] = []
        self._event_counter = 0
        
    def simulate_turn(self, state: Dict[str, Any], days_passed: int = 1) -> List[WorldEvent]:
        """
        Run a simulation turn for the world.
        
        Args:
            state: The current game state dictionary
            days_passed: Number of in-game days to simulate
            
        Returns:
            List of new events generated
        """
        new_events = []
        
        # 1. Simulate Faction Dynamics (chance per day)
        if random.random() < (0.1 * days_passed):
            event = self._simulate_faction_event(state)
            if event:
                new_events.append(event)
        
        # 2. Simulate NPC Lives (very low chance per day)
        if random.random() < (0.01 * days_passed):
            event = self._simulate_npc_event(state)
            if event:
                new_events.append(event)
        
        # Store events
        self.events.extend(new_events)
        
        # Trim history if too long
        if len(self.events) > 100:
            self.events = self.events[-100:]
            
        return new_events
    
    def _create_event(
        self,
        event_type: EventType,
        description: str,
        location: str,
        related_factions: List[str] = None,
        related_npcs: List[str] = None
    ) -> WorldEvent:
        """Create and register a new event."""
        self._event_counter += 1
        event = WorldEvent(
            id=f"evt_{self._event_counter}",
            event_type=event_type,
            description=description,
            location=location,
            related_factions=related_factions or [],
            related_npcs=related_npcs or []
        )
        return event

    def _simulate_faction_event(self, state: Dict[str, Any]) -> Optional[WorldEvent]:
        """Simulate a faction-related event."""
        # This would integrate with the actual faction system
        # For now, we simulate basic events
        factions = ["Iron Syndicate", "Keepers", "Archivists", "Free Traders"]
        
        event_type = random.choice([
            EventType.FACTION_EXPANSION,
            EventType.FACTION_CONTRACTION,
            EventType.FACTION_WAR,
            EventType.DISCOVERY
        ])
        
        faction = random.choice(factions)
        location = "Sector 4"  # Placeholder
        
        if event_type == EventType.FACTION_EXPANSION:
            return self._create_event(
                event_type,
                f"The {faction} have established a new outpost causing tensions to rise.",
                location,
                related_factions=[faction]
            )
        elif event_type == EventType.FACTION_WAR:
            target = random.choice([f for f in factions if f != faction])
            return self._create_event(
                event_type,
                f"Skirmishes reported between {faction} and {target} fleets.",
                location,
                related_factions=[faction, target]
            )
            
        return None

    def _simulate_npc_event(self, state: Dict[str, Any]) -> Optional[WorldEvent]:
        """Simulate an NPC lifecycle event."""
        # Placeholder for NPC simulation
        # In a real implementation, this would iterate over active NPCs
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "events": [e.to_dict() for e in self.events],
            "event_counter": self._event_counter
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldSimulator":
        sim = cls()
        sim.events = [WorldEvent.from_dict(e) for e in data.get("events", [])]
        sim._event_counter = data.get("event_counter", 0)
        return sim
