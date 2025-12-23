"""
Star Map System for Starforged AI Game Master.
Procedurally generates star systems and manages interstellar travel.
"""

from __future__ import annotations

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
    atmosphere: str = "none"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "planet_type": self.planet_type.value,
            "description": self.description,
            "habitable": self.habitable,
            "resources": self.resources,
            "atmosphere": self.atmosphere
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Planet":
        return cls(
            name=data["name"],
            planet_type=PlanetType(data["planet_type"]),
            description=data.get("description", ""),
            habitable=data.get("habitable", False),
            resources=data.get("resources", []),
            atmosphere=data.get("atmosphere", "none")
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
    position: tuple[float, float] = (0.0, 0.0)
    controlling_faction: Optional[str] = None
    
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
            "discovered": self.discovered,
            "position": self.position,
            "controlling_faction": self.controlling_faction,
            "position": list(self.position)
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
            discovered=data.get("discovered", False),
            position=tuple(data.get("position", (0.0, 0.0))),
            controlling_faction=data.get("controlling_faction")
        )


class Sector:
    """A sector containing multiple star systems."""

    def __init__(self, name: str = "Unknown Sector"):
        self.name = name
        self.systems: dict[str, StarSystem] = {}
        self.connections: dict[str, list[str]] = {}

    def add_system(self, system: StarSystem):
        """Add a system to the sector."""
        self.systems[system.id] = system
        self.connections.setdefault(system.id, [])

    def add_connection(self, system_a: str, system_b: str) -> None:
        """Create a bidirectional connection between systems."""
        if system_a not in self.systems or system_b not in self.systems:
            return

        self.connections.setdefault(system_a, [])
        self.connections.setdefault(system_b, [])

        if system_b not in self.connections[system_a]:
            self.connections[system_a].append(system_b)
        if system_a not in self.connections[system_b]:
            self.connections[system_b].append(system_a)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "systems": {k: v.to_dict() for k, v in self.systems.items()},
            "connections": self.connections
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Sector":
        sector = cls(data.get("name", "Unknown Sector"))
        sector.systems = {k: StarSystem.from_dict(v) for k, v in data.get("systems", {}).items()}
        sector.connections = data.get("connections", {k: [] for k in sector.systems})
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

    def get_reachable_systems(self, start_id: str, max_jumps: int = 1) -> list[str]:
        """Return systems reachable within a given number of jumps."""
        if start_id not in self.sector.connections:
            return []

        visited = {start_id}
        frontier = [start_id]

        for _ in range(max_jumps):
            next_frontier: list[str] = []
            for node in frontier:
                for neighbor in self.sector.connections.get(node, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_frontier.append(neighbor)
            frontier = next_frontier
            if not frontier:
                break

        visited.remove(start_id)
        return list(visited)


class StarmapGenerator:
    """Procedurally generates sectors with star systems and connections."""

    def __init__(self, seed: Optional[int] = None):
        self.random = random.Random(seed)

    def generate_sector(self, name: str, num_systems: int = 20) -> Sector:
        sector = Sector(name)

        for i in range(num_systems):
            system_id = f"{name.lower().replace(' ', '_')}_{i:03d}"
            position = (self.random.uniform(0, 100), self.random.uniform(0, 100))
            planets = [self._generate_planet(system_id, j) for j in range(self.random.randint(1, 5))]

            system = StarSystem(
                id=system_id,
                name=self._generate_system_name(),
                star_class=self.random.choice(list(StarClass)),
                planets=planets,
                has_station=self.random.random() < 0.3,
                danger_level=self.random.random(),
                resources=self.random.sample([
                    "Minerals", "Fuel", "Technology", "Organics", "Rare Metals"
                ], k=self.random.randint(1, 3)),
                position=position
            )
            sector.add_system(system)

        self._connect_systems(sector)
        return sector

    def _generate_planet(self, system_name: str, index: int) -> Planet:
        planet_type = self.random.choice(list(PlanetType))
        atmospheres = ["none", "breathable", "toxic", "crushing"]

        return Planet(
            name=f"{system_name}-{index}",
            planet_type=planet_type,
            description=f"A {planet_type.value} world",
            habitable=planet_type == PlanetType.HABITABLE,
            resources=self.random.sample([
                "Minerals", "Fuel", "Technology", "Organics", "Rare Metals"
            ], k=self.random.randint(0, 2)),
            atmosphere=self.random.choice(atmospheres)
        )

    def _generate_system_name(self) -> str:
        prefixes = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Theta"]
        suffixes = ["Prime", "Secundus", "Tertius", "Major", "Minor"]
        names = ["Centauri", "Draconis", "Orionis", "Cygni", "Lyrae", "Aquilae"]

        if self.random.random() < 0.5:
            return f"{self.random.choice(prefixes)} {self.random.choice(names)}"
        else:
            return f"{self.random.choice(names)} {self.random.choice(suffixes)}"

    def _connect_systems(self, sector: Sector) -> None:
        system_ids = list(sector.systems.keys())
        if not system_ids:
            return

        # Ensure each system has at least one connection
        for idx, system_id in enumerate(system_ids):
            target = system_ids[(idx + 1) % len(system_ids)]
            sector.add_connection(system_id, target)

        # Add a few extra random connections for variety
        for _ in range(min(len(system_ids), 5)):
            a, b = self.random.sample(system_ids, 2)
            sector.add_connection(a, b)


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
                resources=random.sample(resource_types, k=random.randint(1, 3)),
                position=(random.uniform(0, 100), random.uniform(0, 100))
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
        distance_cache: dict[tuple[str, str], float] = {}

        def cached_distance(a: StarSystem, b: StarSystem) -> float:
            key = tuple(sorted((a.id, b.id)))
            if key not in distance_cache:
                distance_cache[key] = ((a.position[0] - b.position[0]) ** 2 + (a.position[1] - b.position[1]) ** 2) ** 0.5
            return distance_cache[key]
        
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
                            dist = cached_distance(claimed, candidate)
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
        self.connections: dict[str, list[str]] = {}

    def add_system(self, system: StarSystem):
        """Add a system to the sector."""
        self.systems[system.id] = system
        self.connections.setdefault(system.id, [])

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "systems": {k: v.to_dict() for k, v in self.systems.items()},
            "connections": self.connections,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Sector":
        sector = cls(data.get("name", "Unknown Sector"))
        sector.systems = {k: StarSystem.from_dict(v) for k, v in data.get("systems", {}).items()}
        sector.connections = data.get("connections", {k: [] for k in sector.systems.keys()})
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

    def get_reachable_systems(self, start_id: str, max_jumps: int = 1) -> list[str]:
        """Return systems reachable within a number of jumps using connections graph."""
        if start_id not in self.sector.connections:
            return []

        visited = {start_id}
        frontier = [start_id]
        for _ in range(max_jumps):
            next_frontier: list[str] = []
            for node in frontier:
                for neighbor in self.sector.connections.get(node, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_frontier.append(neighbor)
            frontier = next_frontier
            if not frontier:
                break
        visited.remove(start_id)
        return list(visited)


class StarmapGenerator:
    """Procedurally generates a sector with star systems and connections."""

    def __init__(self, seed: Optional[int] = None):
        self.random = random.Random(seed)

    def generate_sector(self, name: str, num_systems: int = 10) -> Sector:
        sector = Sector(name)

        for i in range(num_systems):
            system = self._generate_system(name, i)
            sector.add_system(system)

        self._generate_connections(sector)
        return sector

    def _generate_system(self, sector_name: str, index: int) -> StarSystem:
        system_id = f"{sector_name.lower().replace(' ', '_')}_{index:03d}"
        star_class = self.random.choice(list(StarClass))
        position = (self.random.uniform(0, 100), self.random.uniform(0, 100))
        planets = [self._generate_planet(system_id, i) for i in range(self.random.randint(1, 5))]

        return StarSystem(
            id=system_id,
            name=self._generate_system_name(),
            star_class=star_class,
            planets=planets,
            has_station=self.random.random() < 0.3,
            danger_level=self.random.random(),
            resources=self.random.sample(
                ["Minerals", "Fuel", "Technology", "Organics", "Rare Metals"],
                k=self.random.randint(1, 3),
            ),
            position=position,
        )

    def _generate_planet(self, system_id: str, index: int) -> Planet:
        planet_type = self.random.choice(list(PlanetType))
        atmospheres = ["none", "breathable", "toxic", "crushing"]

        return Planet(
            name=f"{system_id}-Planet-{index}",
            planet_type=planet_type,
            description=f"A {planet_type.value} world",
            habitable=planet_type == PlanetType.HABITABLE,
            resources=self.random.sample(
                ["Minerals", "Fuel", "Technology", "Organics", "Rare Metals"],
                k=self.random.randint(0, 2),
            ),
            atmosphere=self.random.choice(atmospheres),
        )

    def _generate_connections(self, sector: Sector) -> None:
        # Simple ring connection so each system has at least two neighbors when possible
        system_ids = list(sector.systems.keys())
        for idx, system_id in enumerate(system_ids):
            next_id = system_ids[(idx + 1) % len(system_ids)]
            sector.connections.setdefault(system_id, [])
            sector.connections.setdefault(next_id, [])
            if next_id not in sector.connections[system_id]:
                sector.connections[system_id].append(next_id)
            if system_id not in sector.connections[next_id]:
                sector.connections[next_id].append(system_id)

    def _generate_system_name(self) -> str:
        prefixes = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Theta"]
        suffixes = ["Prime", "Secundus", "Tertius", "Major", "Minor"]
        names = ["Centauri", "Draconis", "Orionis", "Cygni", "Lyrae", "Aquilae"]

        if self.random.random() < 0.5:
            return f"{self.random.choice(prefixes)} {self.random.choice(names)}"
        return f"{self.random.choice(names)} {self.random.choice(suffixes)}"


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
            resources=random.sample(resource_types, k=random.randint(1, 3)),
            position=(random.uniform(0, 100), random.uniform(0, 100)),
        )
        sector.add_system(system)

    # Connect systems in sequence for reachability
    system_ids = list(sector.systems.keys())
    for idx, system_id in enumerate(system_ids):
        if idx + 1 < len(system_ids):
            neighbor = system_ids[idx + 1]
            sector.connections.setdefault(system_id, []).append(neighbor)
            sector.connections.setdefault(neighbor, []).append(system_id)

    # Simple ring connections
    system_ids = list(sector.systems.keys())
    for idx, system_id in enumerate(system_ids):
        neighbor = system_ids[(idx + 1) % len(system_ids)]
        sector.add_connection(system_id, neighbor)

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

