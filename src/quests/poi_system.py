"""
POI (Points of Interest) System

Maintains discovery density (Rule of 30 Seconds) by tracking content clusters
and spawning phase-appropriate quest hooks.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import json
import math
from pathlib import Path


@dataclass
class POI:
    """A point of interest in the world."""
    id: str
    name: str
    location: Tuple[float, float]  # (x, y) coordinates
    poi_type: str  # quest_start, lore, npc, hazard, resource, discovery
    phase: int  # Which phase this POI is available in
    quest_hooks: List[str] = field(default_factory=list)  # Quest IDs this POI can start
    biome: str = ""  # asteroid_field, station, nebula, etc.
    faction: str = ""  # Which faction controls this area
    discovered: bool = False
    description: str = ""
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": list(self.location),
            "poi_type": self.poi_type,
            "phase": self.phase,
            "quest_hooks": self.quest_hooks,
            "biome": self.biome,
            "faction": self.faction,
            "discovered": self.discovered,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "POI":
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            location=tuple(data.get("location", [0, 0])),
            poi_type=data.get("poi_type", "discovery"),
            phase=data.get("phase", 1),
            quest_hooks=data.get("quest_hooks", []),
            biome=data.get("biome", ""),
            faction=data.get("faction", ""),
            discovered=data.get("discovered", False),
            description=data.get("description", "")
        )


class POIHeatmap:
    """
    Manages POI distribution and discovery density.
    
    Ensures players encounter content every ~30 seconds of traversal
    by maintaining a heatmap of content clusters.
    """
    
    def __init__(self):
        self.pois: Dict[str, POI] = {}
        self.current_phase: int = 1
        self.player_location: Tuple[float, float] = (0.0, 0.0)
        self.discovery_radius: float = 50.0  # Distance at which POIs are discovered
        self.density_target: float = 30.0  # Target: one POI every 30 units of travel
    
    def load_from_json(self, filepath: str):
        """Load POIs from JSON file."""
        path = Path(filepath)
        if not path.exists():
            return
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            for poi_data in data.get("pois", []):
                poi = POI.from_dict(poi_data)
                self.pois[poi.id] = poi
    
    def save_to_json(self, filepath: str):
        """Save POIs to JSON file."""
        data = {
            "pois": [poi.to_dict() for poi in self.pois.values()]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_poi(self, poi: POI):
        """Add a POI to the heatmap."""
        self.pois[poi.id] = poi
    
    def distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two locations."""
        return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)
    
    def get_nearby_pois(self, location: Tuple[float, float], 
                        radius: Optional[float] = None,
                        phase: Optional[int] = None,
                        biome: Optional[str] = None,
                        poi_type: Optional[str] = None) -> List[POI]:
        """
        Get POIs near a location with optional filters.
        
        Args:
            location: Center point
            radius: Search radius (defaults to discovery_radius)
            phase: Filter by phase
            biome: Filter by biome
            poi_type: Filter by POI type
        """
        radius = radius or self.discovery_radius
        phase = phase or self.current_phase
        
        nearby = []
        for poi in self.pois.values():
            # Check phase availability
            if poi.phase > phase:
                continue
            
            # Check distance
            dist = self.distance(location, poi.location)
            if dist > radius:
                continue
            
            # Apply filters
            if biome and poi.biome != biome:
                continue
            if poi_type and poi.poi_type != poi_type:
                continue
            
            nearby.append(poi)
        
        # Sort by distance
        nearby.sort(key=lambda p: self.distance(location, p.location))
        return nearby
    
    def discover_pois(self, location: Tuple[float, float]) -> List[POI]:
        """
        Discover POIs near the player's current location.
        
        Returns newly discovered POIs.
        """
        nearby = self.get_nearby_pois(location)
        newly_discovered = []
        
        for poi in nearby:
            if not poi.discovered:
                poi.discovered = True
                newly_discovered.append(poi)
        
        return newly_discovered
    
    def get_quest_hooks_nearby(self, location: Tuple[float, float], 
                                radius: Optional[float] = None) -> List[str]:
        """Get quest IDs that can be started from nearby POIs."""
        nearby = self.get_nearby_pois(location, radius)
        quest_hooks = []
        
        for poi in nearby:
            quest_hooks.extend(poi.quest_hooks)
        
        return list(set(quest_hooks))  # Remove duplicates
    
    def check_density(self, location: Tuple[float, float], 
                      check_radius: float = 100.0) -> Dict[str, any]:
        """
        Check POI density around a location.
        
        Returns density metrics to ensure Rule of 30 Seconds is met.
        """
        nearby = self.get_nearby_pois(location, check_radius)
        
        if not nearby:
            return {
                "density": 0.0,
                "meets_target": False,
                "nearest_poi_distance": None,
                "recommendation": "Add more POIs in this area"
            }
        
        # Calculate average distance between POIs
        distances = [self.distance(location, poi.location) for poi in nearby]
        avg_distance = sum(distances) / len(distances)
        nearest_distance = min(distances)
        
        # Density = POIs per unit area
        area = math.pi * check_radius ** 2
        density = len(nearby) / area
        
        meets_target = nearest_distance <= self.density_target
        
        return {
            "density": density,
            "poi_count": len(nearby),
            "avg_distance": avg_distance,
            "nearest_poi_distance": nearest_distance,
            "meets_target": meets_target,
            "recommendation": "Good density" if meets_target else f"Nearest POI is {nearest_distance:.1f} units away (target: {self.density_target})"
        }
    
    def spawn_phase_pois(self, phase: int):
        """Activate POIs for a new phase."""
        self.current_phase = phase
        # POIs with phase <= current_phase are now available
        # This is handled automatically in get_nearby_pois
    
    def get_undiscovered_count(self, phase: Optional[int] = None) -> int:
        """Get count of undiscovered POIs in current or specified phase."""
        phase = phase or self.current_phase
        count = 0
        for poi in self.pois.values():
            if poi.phase <= phase and not poi.discovered:
                count += 1
        return count
    
    def get_heatmap_summary(self) -> Dict[str, any]:
        """Get summary of POI distribution."""
        by_phase = {}
        by_type = {}
        by_biome = {}
        
        for poi in self.pois.values():
            # Count by phase
            if poi.phase not in by_phase:
                by_phase[poi.phase] = 0
            by_phase[poi.phase] += 1
            
            # Count by type
            if poi.poi_type not in by_type:
                by_type[poi.poi_type] = 0
            by_type[poi.poi_type] += 1
            
            # Count by biome
            if poi.biome:
                if poi.biome not in by_biome:
                    by_biome[poi.biome] = 0
                by_biome[poi.biome] += 1
        
        discovered_count = sum(1 for poi in self.pois.values() if poi.discovered)
        
        return {
            "total_pois": len(self.pois),
            "discovered": discovered_count,
            "undiscovered": len(self.pois) - discovered_count,
            "by_phase": by_phase,
            "by_type": by_type,
            "by_biome": by_biome,
            "current_phase": self.current_phase
        }
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "pois": {poi_id: poi.to_dict() for poi_id, poi in self.pois.items()},
            "current_phase": self.current_phase,
            "player_location": list(self.player_location),
            "discovery_radius": self.discovery_radius,
            "density_target": self.density_target
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "POIHeatmap":
        """Deserialize from dictionary."""
        heatmap = cls()
        heatmap.current_phase = data.get("current_phase", 1)
        heatmap.player_location = tuple(data.get("player_location", [0.0, 0.0]))
        heatmap.discovery_radius = data.get("discovery_radius", 50.0)
        heatmap.density_target = data.get("density_target", 30.0)
        
        for poi_id, poi_data in data.get("pois", {}).items():
            heatmap.pois[poi_id] = POI.from_dict(poi_data)
        
        return heatmap
