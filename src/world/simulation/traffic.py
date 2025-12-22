"""
Traffic System - Space ship movements, trade routes, patrols, congestion.
Manages NPC ship pathing, collision avoidance, and traffic flow.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import math


class ShipType(Enum):
    """Types of ships in traffic."""
    TRADER = "trader"
    PATROL = "patrol"
    CIVILIAN = "civilian"
    PIRATE = "pirate"


@dataclass
class Vector3:
    """3D position/velocity vector."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def distance_to(self, other: Vector3) -> float:
        """Calculate distance to another vector."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def normalize(self) -> Vector3:
        """Return normalized vector."""
        mag = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if mag == 0:
            return Vector3(0, 0, 0)
        return Vector3(self.x/mag, self.y/mag, self.z/mag)


@dataclass
class ShipTraffic:
    """Individual ship in traffic system."""
    ship_id: str
    ship_type: ShipType
    position: Vector3
    velocity: Vector3
    destination: Vector3
    faction: Optional[str] = None
    speed: float = 1.0
    scan_range: float = 1.0
    
    # Patrol-specific
    patrol_route: Optional[List[Vector3]] = None
    route_index: int = 0


@dataclass
class TradeRoute:
    """Defined trade route between sectors."""
    route_id: str
    waypoints: List[Vector3]
    traffic_density: float  # 0.0-1.0
    faction_controlled: Optional[str] = None


@dataclass
class PatrolRoute:
    """Faction patrol route."""
    faction: str
    waypoints: List[Vector3]
    patrol_frequency: float  # Ships per hour
    scan_range: float


class TrafficSystem:
    """Manages space traffic simulation."""
    
    def __init__(self, config):
        self.config = config
        self.active_ships: Dict[str, ShipTraffic] = {}
        self.trade_routes: List[TradeRoute] = []
        self.patrol_routes: Dict[str, PatrolRoute] = {}
        self.congestion_map: Dict[str, float] = {}  # sector_id -> congestion
        self._ship_counter = 0
    
    def tick(self, delta_time: float, current_sector: str, player_position: Vector3) -> List[Dict]:
        """
        Update traffic simulation.
        
        Args:
            delta_time: Time elapsed in hours
            current_sector: Player's current sector ID
            player_position: Player's position
            
        Returns:
            List of traffic events
        """
        events = []
        
        # Update existing ships
        for ship_id, ship in list(self.active_ships.items()):
            # Move ship toward destination
            self._move_ship(ship, delta_time)
            
            # Check if reached destination
            if ship.position.distance_to(ship.destination) < 0.5:
                if ship.ship_type == ShipType.PATROL and ship.patrol_route:
                    # Move to next waypoint
                    ship.route_index = (ship.route_index + 1) % len(ship.patrol_route)
                    ship.destination = ship.patrol_route[ship.route_index]
                else:
                    # Remove ship
                    del self.active_ships[ship_id]
                    continue
            
            # Collision avoidance
            self._apply_avoidance(ship, player_position)
        
        # Spawn new ships based on trade routes
        if random.random() < self.config.trade_route_density * delta_time:
            new_ship = self._spawn_trade_ship(current_sector)
            if new_ship:
                self.active_ships[new_ship.ship_id] = new_ship
                events.append({
                    "type": "traffic_spawn",
                    "ship_type": new_ship.ship_type.value,
                    "sector": current_sector
                })
        
        # Spawn patrol ships
        for faction, patrol in self.patrol_routes.items():
            if random.random() < patrol.patrol_frequency * delta_time * self.config.patrol_frequency_multiplier:
                new_ship = self._spawn_patrol_ship(faction, patrol)
                if new_ship:
                    self.active_ships[new_ship.ship_id] = new_ship
                    events.append({
                        "type": "patrol_spawn",
                        "faction": faction,
                        "sector": current_sector
                    })
        
        # Update congestion
        self._update_congestion(current_sector)
        
        # Check for congestion events
        if self.congestion_map.get(current_sector, 0.0) > self.config.congestion_threshold_high:
            events.append({
                "type": "traffic_congestion",
                "sector": current_sector,
                "congestion_level": "high"
            })
        
        # Patrol scans
        for ship in self.active_ships.values():
            if ship.ship_type == ShipType.PATROL:
                if ship.position.distance_to(player_position) < ship.scan_range:
                    events.append({
                        "type": "patrol_scan",
                        "faction": ship.faction,
                        "ship_id": ship.ship_id
                    })
        
        return events
    
    def _move_ship(self, ship: ShipTraffic, delta_time: float):
        """Move ship toward destination."""
        # Calculate direction
        dx = ship.destination.x - ship.position.x
        dy = ship.destination.y - ship.position.y
        dz = ship.destination.z - ship.position.z
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        if distance < 0.01:
            return
        
        # Normalize and apply speed
        move_distance = ship.speed * delta_time
        if move_distance > distance:
            move_distance = distance
        
        ship.position.x += (dx / distance) * move_distance
        ship.position.y += (dy / distance) * move_distance
        ship.position.z += (dz / distance) * move_distance
    
    def _apply_avoidance(self, ship: ShipTraffic, player_position: Vector3):
        """Apply collision avoidance behavior."""
        # Check distance to player
        dist_to_player = ship.position.distance_to(player_position)
        
        if dist_to_player < self.config.emergency_stop_distance:
            # Emergency stop
            ship.velocity = Vector3(0, 0, 0)
        elif dist_to_player < self.config.avoidance_distance:
            # Slow down and adjust course slightly
            ship.speed *= 0.7
    
    def _spawn_trade_ship(self, sector: str) -> Optional[ShipTraffic]:
        """Spawn a new trade ship."""
        if len(self.active_ships) >= self.config.max_ships_per_sector:
            return None
        
        self._ship_counter += 1
        
        # Random start and end positions (simplified)
        start = Vector3(
            random.uniform(-10, 10),
            random.uniform(-10, 10),
            random.uniform(-10, 10)
        )
        end = Vector3(
            random.uniform(-10, 10),
            random.uniform(-10, 10),
            random.uniform(-10, 10)
        )
        
        return ShipTraffic(
            ship_id=f"trade_{self._ship_counter}",
            ship_type=ShipType.TRADER,
            position=start,
            velocity=Vector3(0, 0, 0),
            destination=end,
            speed=self.config.trade_ship_speed
        )
    
    def _spawn_patrol_ship(self, faction: str, patrol: PatrolRoute) -> Optional[ShipTraffic]:
        """Spawn a patrol ship on a route."""
        if len(self.active_ships) >= self.config.max_ships_per_sector:
            return None
        
        self._ship_counter += 1
        
        # Start at first waypoint
        start_waypoint = patrol.waypoints[0]
        
        return ShipTraffic(
            ship_id=f"patrol_{faction}_{self._ship_counter}",
            ship_type=ShipType.PATROL,
            position=Vector3(start_waypoint.x, start_waypoint.y, start_waypoint.z),
            velocity=Vector3(0, 0, 0),
            destination=patrol.waypoints[1] if len(patrol.waypoints) > 1 else start_waypoint,
            faction=faction,
            speed=1.0,
            scan_range=patrol.scan_range,
            patrol_route=patrol.waypoints,
            route_index=0
        )
    
    def _update_congestion(self, sector: str):
        """Update congestion level for sector."""
        ship_count = len(self.active_ships)
        max_ships = self.config.max_ships_per_sector
        
        congestion = min(1.0, ship_count / max_ships)
        self.congestion_map[sector] = congestion
    
    def add_trade_route(self, route: TradeRoute):
        """Add a trade route to the system."""
        self.trade_routes.append(route)
    
    def add_patrol_route(self, faction: str, route: PatrolRoute):
        """Add a patrol route for a faction."""
        self.patrol_routes[faction] = route
    
    def get_congestion(self, sector: str) -> float:
        """Get current congestion level for a sector."""
        return self.congestion_map.get(sector, 0.0)
    
    def get_nearby_ships(self, position: Vector3, radius: float) -> List[ShipTraffic]:
        """Get all ships within radius of position."""
        nearby = []
        for ship in self.active_ships.values():
            if ship.position.distance_to(position) <= radius:
                nearby.append(ship)
        return nearby
    
    def to_dict(self) -> Dict:
        """Serialize state."""
        return {
            "active_ships": {
                ship_id: {
                    "ship_type": ship.ship_type.value,
                    "position": [ship.position.x, ship.position.y, ship.position.z],
                    "faction": ship.faction
                }
                for ship_id, ship in self.active_ships.items()
            },
            "congestion_map": self.congestion_map,
            "ship_counter": self._ship_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict, config) -> TrafficSystem:
        """Deserialize state."""
        system = cls(config)
        system._ship_counter = data.get("ship_counter", 0)
        system.congestion_map = data.get("congestion_map", {})
        # Note: Active ships are transient, not restored
        return system
