"""
Star Map System for Starforged AI Game Master.
Procedurally generates star systems and manages interstellar travel.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import random


class StarClass(Enum):
    """Star classification types."""
    RED_DWARF = "red_dwarf"
    YELLOW_STAR = "yellow_star"
    BLUE_GIANT = "blue_giant"
    WHITE_DWARF = "white_dwarf"
    BINARY_SYSTEM = "binary_system"


class PlanetType(Enum):
    """Planet types."""
    BARREN = "barren"
    ICE = "ice"
    DESERT = "desert"
    OCEAN = "ocean"
    JUNGLE = "jungle"
    VOLCANIC = "volcanic"
    GAS_GIANT = "gas_giant"
    HABITABLE = "habitable"


@dataclass
class Planet:
    """A planet in a star system."""
    name: str
    planet_type: PlanetType
    description: str = ""
    habitable: bool = False
    resources: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "planet_type": self.planet_type.value,
            "description": self.description,
            "habitable": self.habitable,
            "resources": self.resources
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Planet":
        return cls(
            name=data["name"],
            planet_type=PlanetType(data["planet_type"]),
            description=data.get("description", ""),
            habitable=data.get("habitable", False),
            resources=data.get("resources", [])
        )


@dataclass
class StarSystem:
    """A single star system in the sector."""
    id: str
    name: str
    star_class: StarClass
    planets: list[Planet] = field(default_factory=list)
    has_station: bool = False
    danger_level: float = 0.0  # 0.0 to 1.0
    resources: list[str] = field(default_factory=list)
    discovered: bool = False
    
    # Legacy compatibility
    @property
    def star_type(self) -> str:
        return self.star_class.value.replace("_", " ").title()
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "star_class": self.star_class.value,
            "star_type": self.star_type,  # For compatibility
            "planets": [p.to_dict() for p in self.planets],
            "has_station": self.has_station,
            "danger_level": self.danger_level,
            "resources": self.resources,
            "discovered": self.discovered
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StarSystem":
        return cls(
            id=data["id"],
            name=data["name"],
            star_class=StarClass(data.get("star_class", "yellow_star")),
            planets=[Planet.from_dict(p) for p in data.get("planets", [])],
            has_station=data.get("has_station", False),
            danger_level=data.get("danger_level", 0.0),
            resources=data.get("resources", []),
            discovered=data.get("discovered", False)
        )


class StarMap:
    """Manages the procedural star map."""
    
    def __init__(self):
        self.systems: dict[str, StarSystem] = {}
        self.current_system_id: str = ""
        self.discovered_systems: list[str] = []
        self.travel_history: list[str] = []
        
    def generate_sector(self, sector_name: str, system_count: int = 20):
        """Generate a new sector with random systems."""
        star_classes = list(StarClass)
        planet_types = list(PlanetType)
        resource_types = ["Minerals", "Fuel", "Technology", "Organics", "Rare Metals"]
        
        for i in range(system_count):
            system_id = f"{sector_name}_{i:03d}"
            
            # Generate planets
            num_planets = random.randint(0, 5)
            planets = []
            for p in range(num_planets):
                planet_type = random.choice(planet_types)
                planet = Planet(
                    name=f"Planet {chr(65 + p)}",
                    planet_type=planet_type,
                    description=f"A {planet_type.value} world",
                    habitable=planet_type == PlanetType.HABITABLE,
                    resources=random.sample(resource_types, k=random.randint(0, 2))
                )
                planets.append(planet)
            
            system = StarSystem(
                id=system_id,
                name=self._generate_system_name(),
                star_class=random.choice(star_classes),
                planets=planets,
                has_station=random.random() < 0.3,
                danger_level=random.random(),
                resources=random.sample(resource_types, k=random.randint(1, 3))
            )
            self.systems[system_id] = system
            
    def assign_faction_territories(self, sector: Sector, factions: list[dict[str, Any]]) -> None:
        """
        Assign territories to factions based on their influence.
        
        Args:
            sector: The sector to assign territories in
            factions: List of faction dictionaries with 'id' and 'influence' (0.0-1.0)
        """
        if not factions or not sector.systems:
            return
            
        # Sort factions by influence (highest first)
        sorted_factions = sorted(
            factions, 
            key=lambda x: x.get('influence', 0.5), 
            reverse=True
        )
        
        # Calculate target number of systems for each faction
        total_systems = len(sector.systems)
        unclaimed_systems = list(sector.systems.values())
        
        for faction in sorted_factions:
            faction_id = faction['id']
            influence = faction.get('influence', 0.5)
            
            # Target count based on influence (e.g., 0.5 influence = 50% of REMAINING systems)
            # We use remaining systems to ensure everyone gets a chance, but higher influence picks first
            target_count = max(1, int(len(unclaimed_systems) * influence * 0.5))
            
            if not unclaimed_systems:
                break
                
            # Pick a starting system (seed)
            seed_system = random.choice(unclaimed_systems)
            seed_system.controlling_faction = faction_id
            unclaimed_systems.remove(seed_system)
            
            systems_claimed = [seed_system]
            
            # Expand from seed to neighbors
            # Note: This uses simple proximity since we don't have a graph unless we build it
            # For now, we'll pick closest systems
            
            while len(systems_claimed) < target_count and unclaimed_systems:
                # Find closest unclaimed system to any claimed system
                best_candidate = None
                min_dist = float('inf')
                
                for claimed in systems_claimed:
                    for candidate in unclaimed_systems:
                        # Simple distance calculation (assuming positions exist, if not we pick random)
                        if hasattr(claimed, 'position') and hasattr(candidate, 'position'):
                            dist = ((claimed.position[0] - candidate.position[0])**2 + 
                                   (claimed.position[1] - candidate.position[1])**2)**0.5
                            if dist < min_dist:
                                min_dist = dist
                                best_candidate = candidate
                
                if best_candidate:
                    best_candidate.controlling_faction = faction_id
                    unclaimed_systems.remove(best_candidate)
                    systems_claimed.append(best_candidate)
                else:
                    # Fallback if no positions
                    next_sys = unclaimed_systems.pop(0)
                    next_sys.controlling_faction = faction_id
                    systems_claimed.append(next_sys)

        # Remaining systems are independent/neutral
        for system in unclaimed_systems:
            system.controlling_faction = "neutral"

    def _generate_system_name(self) -> str:
        """Generate a procedural system name."""
        prefixes = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Theta"]
        suffixes = ["Prime", "Secundus", "Tertius", "Major", "Minor"]
        names = ["Centauri", "Draconis", "Orionis", "Cygni", "Lyrae", "Aquilae"]
        
        if random.random() < 0.5:
            return f"{random.choice(prefixes)} {random.choice(names)}"
        else:
            return f"{random.choice(names)} {random.choice(suffixes)}"
    
    def travel_to(self, system_id: str) -> dict[str, Any]:
        """Travel to a system and mark it as discovered."""
        if system_id not in self.systems:
            return {"success": False, "error": "System not found"}
        
        system = self.systems[system_id]
        
        # Mark as discovered
        if not system.discovered:
            system.discovered = True
            self.discovered_systems.append(system_id)
        
        # Update travel history
        self.current_system_id = system_id
        self.travel_history.append(system_id)
        
        return {
            "success": True,
            "system": system.to_dict(),
            "travel_time": random.randint(1, 5)  # Days
        }
    
    def get_nearby_systems(self, count: int = 5) -> list[dict]:
        """Get nearby systems for navigation."""
        if not self.current_system_id:
            # Return random systems if no current location
            return [s.to_dict() for s in random.sample(list(self.systems.values()), min(count, len(self.systems)))]
        
        # Simple proximity: return random systems (could be enhanced with actual coordinates)
        available = [s for s in self.systems.values() if s.id != self.current_system_id]
        return [s.to_dict() for s in random.sample(available, min(count, len(available)))]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "systems": {k: v.to_dict() for k, v in self.systems.items()},
            "current_system_id": self.current_system_id,
            "discovered_systems": self.discovered_systems,
            "travel_history": self.travel_history
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StarMap":
        starmap = cls()
        starmap.systems = {k: StarSystem.from_dict(v) for k, v in data.get("systems", {}).items()}
        starmap.current_system_id = data.get("current_system_id", "")
        starmap.discovered_systems = data.get("discovered_systems", [])
        starmap.travel_history = data.get("travel_history", [])
        return starmap


# ============================================================================
# Sector & Route Planning
# ============================================================================

class Sector:
    """A sector containing multiple star systems."""
    
    def __init__(self, name: str = "Unknown Sector"):
        self.name = name
        self.systems: dict[str, StarSystem] = {}
    
    def add_system(self, system: StarSystem):
        """Add a system to the sector."""
        self.systems[system.id] = system
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "systems": {k: v.to_dict() for k, v in self.systems.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Sector":
        sector = cls(data.get("name", "Unknown Sector"))
        sector.systems = {k: StarSystem.from_dict(v) for k, v in data.get("systems", {}).items()}
        return sector


class RoutePlanner:
    """Plans routes between star systems."""
    
    def __init__(self, sector: Sector):
        self.sector = sector
    
    def find_route(self, start_id: str, end_id: str) -> Optional[list[str]]:
        """
        Find a route between two systems.
        Simple implementation - returns direct path.
        Could be enhanced with pathfinding algorithms.
        """
        if start_id not in self.sector.systems or end_id not in self.sector.systems:
            return None
        
        # Simple direct route
        return [start_id, end_id]


def generate_default_sector() -> Sector:
    """Generate a default starting sector with some systems."""
    sector = Sector("The Forge")
    
    star_classes = list(StarClass)
    planet_types = list(PlanetType)
    resource_types = ["Minerals", "Fuel", "Technology", "Organics", "Rare Metals"]
    
    # Generate 10 systems
    for i in range(10):
        system_id = f"forge_{i:03d}"
        
        # Generate planets
        num_planets = random.randint(0, 5)
        planets = []
        for p in range(num_planets):
            planet_type = random.choice(planet_types)
            planet = Planet(
                name=f"Planet {chr(65 + p)}",  # A, B, C, etc.
                planet_type=planet_type,
                description=f"A {planet_type.value} world",
                habitable=planet_type == PlanetType.HABITABLE,
                resources=random.sample(resource_types, k=random.randint(0, 2))
            )
            planets.append(planet)
        
        system = StarSystem(
            id=system_id,
            name=_generate_system_name(),
            star_class=random.choice(star_classes),
            planets=planets,
            has_station=random.random() < 0.3,
            danger_level=random.random(),
            resources=random.sample(resource_types, k=random.randint(1, 3))
        )
        sector.add_system(system)
    
    return sector


def _generate_system_name() -> str:
    """Generate a procedural system name."""
    prefixes = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Theta"]
    suffixes = ["Prime", "Secundus", "Tertius", "Major", "Minor"]
    names = ["Centauri", "Draconis", "Orionis", "Cygni", "Lyrae", "Aquilae"]
    
    if random.random() < 0.5:
        return f"{random.choice(prefixes)} {random.choice(names)}"
    else:
        return f"{random.choice(names)} {random.choice(suffixes)}"

