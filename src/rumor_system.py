"""
Rumor & Information Network for Starforged AI Game Master.

Tracks rumors, their sources, accuracy, and decay over time.
Rumors spread between locations and NPCs.
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

class RumorType(Enum):
    """Types of rumors."""
    THREAT = "threat"
    OPPORTUNITY = "opportunity"
    FACTION_NEWS = "faction_news"
    NPC_GOSSIP = "npc_gossip"
    LOCATION_INFO = "location_info"
    RESOURCE = "resource"


class RumorSource(Enum):
    """Source reliability levels."""
    UNRELIABLE = "unreliable"  # 30% accuracy
    QUESTIONABLE = "questionable"  # 50% accuracy
    CREDIBLE = "credible"  # 70% accuracy
    VERIFIED = "verified"  # 90% accuracy


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Rumor:
    """A piece of information circulating in the world."""
    id: str
    content: str
    rumor_type: RumorType
    source_reliability: RumorSource
    accuracy: float  # 0.0-1.0, actual truth value
    location_origin: str  # Where it started
    current_locations: List[str] = field(default_factory=list)  # Where it's known
    age_scenes: int = 0  # How old the rumor is
    decay_rate: float = 0.1  # How fast it becomes outdated
    is_outdated: bool = False
    related_npc: Optional[str] = None
    related_faction: Optional[str] = None
    related_system: Optional[str] = None
    
    def get_reliability_modifier(self) -> float:
        """Get accuracy modifier based on source."""
        modifiers = {
            RumorSource.UNRELIABLE: 0.3,
            RumorSource.QUESTIONABLE: 0.5,
            RumorSource.CREDIBLE: 0.7,
            RumorSource.VERIFIED: 0.9,
        }
        return modifiers.get(self.source_reliability, 0.5)
    
    def is_accurate(self) -> bool:
        """Check if this rumor is actually true."""
        return random.random() < (self.accuracy * self.get_reliability_modifier())
    
    def age(self) -> None:
        """Age the rumor by one scene."""
        self.age_scenes += 1
        
        # Chance to become outdated
        if random.random() < self.decay_rate:
            self.is_outdated = True
    
    def spread_to(self, location: str) -> None:
        """Spread rumor to a new location."""
        if location not in self.current_locations:
            self.current_locations.append(location)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "rumor_type": self.rumor_type.value,
            "source_reliability": self.source_reliability.value,
            "accuracy": self.accuracy,
            "location_origin": self.location_origin,
            "current_locations": self.current_locations,
            "age_scenes": self.age_scenes,
            "decay_rate": self.decay_rate,
            "is_outdated": self.is_outdated,
            "related_npc": self.related_npc,
            "related_faction": self.related_faction,
            "related_system": self.related_system,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Rumor":
        return cls(
            id=data["id"],
            content=data["content"],
            rumor_type=RumorType(data["rumor_type"]),
            source_reliability=RumorSource(data["source_reliability"]),
            accuracy=data["accuracy"],
            location_origin=data["location_origin"],
            current_locations=data.get("current_locations", []),
            age_scenes=data.get("age_scenes", 0),
            decay_rate=data.get("decay_rate", 0.1),
            is_outdated=data.get("is_outdated", False),
            related_npc=data.get("related_npc"),
            related_faction=data.get("related_faction"),
            related_system=data.get("related_system"),
        )


# ============================================================================
# Rumor Network
# ============================================================================

class RumorNetwork:
    """Manages rumor propagation and decay."""
    
    def __init__(self):
        self.rumors: Dict[str, Rumor] = {}
        self._rumor_counter = 0
    
    def create_rumor(
        self,
        content: str,
        rumor_type: RumorType,
        location: str,
        source_reliability: RumorSource = RumorSource.QUESTIONABLE,
        accuracy: float = 0.5,
        **kwargs
    ) -> Rumor:
        """Create a new rumor."""
        self._rumor_counter += 1
        rumor_id = f"rumor_{self._rumor_counter}"
        
        rumor = Rumor(
            id=rumor_id,
            content=content,
            rumor_type=rumor_type,
            source_reliability=source_reliability,
            accuracy=accuracy,
            location_origin=location,
            current_locations=[location],
            **kwargs
        )
        
        self.rumors[rumor_id] = rumor
        return rumor
    
    def get_rumors_at_location(
        self,
        location: str,
        include_outdated: bool = False
    ) -> List[Rumor]:
        """Get all rumors known at a location."""
        rumors = []
        for rumor in self.rumors.values():
            if location in rumor.current_locations:
                if include_outdated or not rumor.is_outdated:
                    rumors.append(rumor)
        return rumors
    
    def spread_rumors(
        self,
        from_location: str,
        to_location: str,
        spread_chance: float = 0.3
    ) -> List[Rumor]:
        """
        Spread rumors from one location to another.
        
        Args:
            from_location: Source location
            to_location: Destination location
            spread_chance: Probability each rumor spreads
        
        Returns:
            List of rumors that spread
        """
        spread_rumors = []
        
        for rumor in self.get_rumors_at_location(from_location):
            if random.random() < spread_chance:
                rumor.spread_to(to_location)
                spread_rumors.append(rumor)
        
        return spread_rumors
    
    def age_all_rumors(self) -> None:
        """Age all rumors by one scene."""
        for rumor in self.rumors.values():
            rumor.age()
    
    def plant_disinformation(
        self,
        content: str,
        location: str,
        rumor_type: RumorType = RumorType.FACTION_NEWS
    ) -> Rumor:
        """Plant false information (accuracy = 0.0)."""
        return self.create_rumor(
            content=content,
            rumor_type=rumor_type,
            location=location,
            source_reliability=RumorSource.CREDIBLE,  # Seems credible but is false
            accuracy=0.0
        )
    
    def verify_rumor(self, rumor_id: str) -> None:
        """Mark a rumor as verified (increase reliability)."""
        if rumor_id in self.rumors:
            self.rumors[rumor_id].source_reliability = RumorSource.VERIFIED
    
    def invalidate_rumor(self, rumor_id: str) -> None:
        """Mark a rumor as outdated."""
        if rumor_id in self.rumors:
            self.rumors[rumor_id].is_outdated = True
    
    def get_rumors_by_type(
        self,
        rumor_type: RumorType,
        location: Optional[str] = None
    ) -> List[Rumor]:
        """Get rumors of a specific type."""
        rumors = []
        for rumor in self.rumors.values():
            if rumor.rumor_type == rumor_type and not rumor.is_outdated:
                if location is None or location in rumor.current_locations:
                    rumors.append(rumor)
        return rumors
    
    def get_narrator_context(self, location: str) -> str:
        """Generate context for narrator about available rumors."""
        rumors = self.get_rumors_at_location(location)
        
        if not rumors:
            return ""
        
        lines = ["[RUMORS AVAILABLE AT THIS LOCATION]"]
        
        for rumor in rumors[:5]:  # Limit to 5 most recent
            reliability = rumor.source_reliability.value.upper()
            lines.append(f"- [{reliability}] {rumor.content}")
            if rumor.is_outdated:
                lines.append("  (This information may be outdated)")
        
        lines.append("")
        lines.append("RUMOR MECHANICS:")
        lines.append("- Players can ask NPCs about rumors")
        lines.append("- Unreliable sources may provide false information")
        lines.append("- Rumors age and become outdated over time")
        lines.append("- Investigating rumors can lead to quests or dangers")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rumors": {k: v.to_dict() for k, v in self.rumors.items()},
            "rumor_counter": self._rumor_counter,
        }
    
    def generate_rumor(self, source: str, category: str = None) -> Rumor:
        """Procedurally generate a rumor using RumorGenerator."""
        generator = RumorGenerator()
        
        # Decide type
        if category == "threat":
            rtype = RumorType.THREAT
            content = generator.generate_threat_rumor(system="The Forge")
        elif category == "opportunity":
            rtype = RumorType.OPPORTUNITY
            content = generator.generate_opportunity_rumor(system="The Forge")
        else:
            rtype = RumorType.FACTION_NEWS
            content = generator.generate_faction_rumor(faction="Iron Syndicate")
            
        return self.create_rumor(
            content=content,
            rumor_type=rtype,
            location="The Forge",
            source_reliability=RumorSource.QUESTIONABLE,
            accuracy=0.5
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RumorNetwork":
        network = cls()
        network.rumors = {k: Rumor.from_dict(v) for k, v in data.get("rumors", {}).items()}
        network._rumor_counter = data.get("rumor_counter", 0)
        return network


# ============================================================================
# Rumor Generator
# ============================================================================

class RumorGenerator:
    """Generates procedural rumors based on world state."""
    
    THREAT_TEMPLATES = [
        "Pirates have been spotted near {system}",
        "A derelict ship was found drifting in {system} - crew missing",
        "Radiation levels are spiking in the {system} sector",
        "Something is hunting ships near {system}",
        "The {faction} fleet is mobilizing near {system}",
    ]
    
    OPPORTUNITY_TEMPLATES = [
        "Salvage opportunities reported in {system}",
        "The {faction} is hiring mercenaries for work in {system}",
        "Rare resources discovered on {planet}",
        "A settlement in {system} needs supplies urgently",
        "Ancient ruins found on {planet} - untouched",
    ]
    
    FACTION_TEMPLATES = [
        "The {faction} and {faction2} are on the brink of war",
        "{faction} has claimed {system} as their territory",
        "Leadership change in {faction} - new policies expected",
        "{faction} trade routes are being disrupted",
        "Alliance forming between {faction} and {faction2}",
    ]
    
    def generate_threat_rumor(
        self,
        system: str,
        faction: Optional[str] = None
    ) -> str:
        """Generate a threat rumor."""
        template = random.choice(self.THREAT_TEMPLATES)
        return template.format(system=system, faction=faction or "Unknown")
    
    def generate_opportunity_rumor(
        self,
        system: str,
        planet: Optional[str] = None,
        faction: Optional[str] = None
    ) -> str:
        """Generate an opportunity rumor."""
        template = random.choice(self.OPPORTUNITY_TEMPLATES)
        return template.format(
            system=system,
            planet=planet or f"{system} Prime",
            faction=faction or "Local Guild"
        )
    
    def generate_faction_rumor(
        self,
        faction: str,
        faction2: Optional[str] = None,
        system: Optional[str] = None
    ) -> str:
        """Generate a faction-related rumor."""
        template = random.choice(self.FACTION_TEMPLATES)
        return template.format(
            faction=faction,
            faction2=faction2 or "rival faction",
            system=system or "the sector"
        )


# ============================================================================
# Convenience Functions
# ============================================================================

def create_rumor_network() -> RumorNetwork:
    """Create a new rumor network."""
    return RumorNetwork()
