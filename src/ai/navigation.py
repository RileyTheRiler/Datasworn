"""
Navigation System with Spatial Reservations

Manages pathfinding and prop/space reservations to prevent NPC pileups.
Includes cooldown system for reusing the same spots.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum


class PropType(Enum):
    """Types of reservable props/spaces"""
    CHAIR = "chair"
    TABLE = "table"
    STALL = "stall"
    WORKSTATION = "workstation"
    GATE_POST = "gate_post"
    COUNTER = "counter"
    BED = "bed"
    GENERIC = "generic"


@dataclass
class Reservation:
    """A reservation for a prop or space"""
    prop_id: str
    npc_id: str
    reserved_at: datetime
    duration: int  # minutes, 0 = indefinite
    cooldown: int = 0  # seconds before prop can be reused
    
    def is_expired(self, current_time: datetime) -> bool:
        """Check if reservation has expired"""
        if self.duration == 0:
            return False  # Indefinite reservation
        elapsed = (current_time - self.reserved_at).total_seconds() / 60
        return elapsed >= self.duration
    
    def can_reuse(self, current_time: datetime) -> bool:
        """Check if prop can be reused (cooldown expired)"""
        if self.cooldown == 0:
            return True
        elapsed = (current_time - self.reserved_at).total_seconds()
        return elapsed >= self.cooldown


@dataclass
class PropCooldown:
    """Cooldown tracker for a prop"""
    prop_id: str
    last_used_by: str
    last_used_at: datetime
    cooldown_seconds: int
    
    def is_ready(self, current_time: datetime) -> bool:
        """Check if cooldown has expired"""
        elapsed = (current_time - self.last_used_at).total_seconds()
        return elapsed >= self.cooldown_seconds


@dataclass
class PathNode:
    """A node in a navigation path"""
    location: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    connections: List[str] = field(default_factory=list)


class NavigationManager:
    """
    Manages spatial reservations and pathfinding for NPCs.
    
    Features:
    - Reserve props/spaces to prevent conflicts
    - Cooldown system for prop reuse
    - Simple pathfinding (can be extended to A*)
    - Alternative prop suggestions
    """
    
    def __init__(self):
        self.reservations: Dict[str, Reservation] = {}  # prop_id -> reservation
        self.cooldowns: Dict[str, PropCooldown] = {}  # prop_id -> cooldown
        self.navigation_graph: Dict[str, PathNode] = {}  # location -> node
        self.prop_alternatives: Dict[str, List[str]] = {}  # prop_id -> alternative props
    
    def reserve_prop(
        self,
        npc_id: str,
        prop_id: str,
        duration: int = 0,
        cooldown: int = 0,
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Reserve a prop or space for an NPC.
        
        Args:
            npc_id: NPC making the reservation
            prop_id: Prop/space to reserve
            duration: Duration in minutes (0 = indefinite)
            cooldown: Cooldown in seconds before prop can be reused
            current_time: Current game time
        
        Returns:
            True if reservation successful, False if prop unavailable
        """
        current_time = current_time or datetime.now()
        
        # Check if prop is available
        if not self.is_available(prop_id, current_time):
            return False
        
        # Check cooldown
        if prop_id in self.cooldowns:
            if not self.cooldowns[prop_id].is_ready(current_time):
                return False
        
        # Create reservation
        reservation = Reservation(
            prop_id=prop_id,
            npc_id=npc_id,
            reserved_at=current_time,
            duration=duration,
            cooldown=cooldown,
        )
        
        self.reservations[prop_id] = reservation
        return True
    
    def release_prop(
        self,
        npc_id: str,
        prop_id: str,
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Release a prop reservation.
        
        Args:
            npc_id: NPC releasing the reservation
            prop_id: Prop to release
            current_time: Current game time
        
        Returns:
            True if released, False if not reserved by this NPC
        """
        current_time = current_time or datetime.now()
        
        if prop_id not in self.reservations:
            return False
        
        reservation = self.reservations[prop_id]
        if reservation.npc_id != npc_id:
            return False  # Not reserved by this NPC
        
        # Set cooldown if specified
        if reservation.cooldown > 0:
            self.cooldowns[prop_id] = PropCooldown(
                prop_id=prop_id,
                last_used_by=npc_id,
                last_used_at=current_time,
                cooldown_seconds=reservation.cooldown,
            )
        
        # Remove reservation
        del self.reservations[prop_id]
        return True
    
    def is_available(
        self,
        prop_id: str,
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Check if a prop is available for reservation.
        
        Args:
            prop_id: Prop to check
            current_time: Current game time
        
        Returns:
            True if available, False otherwise
        """
        current_time = current_time or datetime.now()
        
        # Check if reserved
        if prop_id in self.reservations:
            reservation = self.reservations[prop_id]
            if not reservation.is_expired(current_time):
                return False  # Still reserved
            else:
                # Expired, remove it
                del self.reservations[prop_id]
        
        # Check cooldown
        if prop_id in self.cooldowns:
            if not self.cooldowns[prop_id].is_ready(current_time):
                return False  # Still on cooldown
            else:
                # Cooldown expired, remove it
                del self.cooldowns[prop_id]
        
        return True
    
    def get_reservation(self, prop_id: str) -> Optional[Reservation]:
        """Get the current reservation for a prop"""
        return self.reservations.get(prop_id)
    
    def get_npc_reservations(self, npc_id: str) -> List[str]:
        """Get all props reserved by an NPC"""
        return [
            prop_id for prop_id, res in self.reservations.items()
            if res.npc_id == npc_id
        ]
    
    def find_alternative(
        self,
        prop_id: str,
        current_time: Optional[datetime] = None
    ) -> Optional[str]:
        """
        Find an alternative prop if the requested one is unavailable.
        
        Args:
            prop_id: Original prop
            current_time: Current game time
        
        Returns:
            Alternative prop ID or None
        """
        current_time = current_time or datetime.now()
        
        # Check registered alternatives
        if prop_id in self.prop_alternatives:
            for alt_prop in self.prop_alternatives[prop_id]:
                if self.is_available(alt_prop, current_time):
                    return alt_prop
        
        return None
    
    def register_alternatives(self, prop_id: str, alternatives: List[str]) -> None:
        """Register alternative props for a given prop"""
        self.prop_alternatives[prop_id] = alternatives
    
    def add_navigation_node(
        self,
        location: str,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        connections: Optional[List[str]] = None
    ) -> None:
        """Add a node to the navigation graph"""
        node = PathNode(
            location=location,
            x=x,
            y=y,
            z=z,
            connections=connections or [],
        )
        self.navigation_graph[location] = node
    
    def get_path(
        self,
        from_location: str,
        to_location: str
    ) -> Optional[List[str]]:
        """
        Get a path from one location to another.
        
        Simple BFS pathfinding. Can be extended to A* for better performance.
        
        Args:
            from_location: Starting location
            to_location: Destination location
        
        Returns:
            List of location names forming the path, or None if no path found
        """
        if from_location not in self.navigation_graph or to_location not in self.navigation_graph:
            return None
        
        if from_location == to_location:
            return [from_location]
        
        # BFS
        queue = [(from_location, [from_location])]
        visited: Set[str] = {from_location}
        
        while queue:
            current, path = queue.pop(0)
            node = self.navigation_graph[current]
            
            for neighbor in node.connections:
                if neighbor in visited:
                    continue
                
                new_path = path + [neighbor]
                
                if neighbor == to_location:
                    return new_path
                
                visited.add(neighbor)
                queue.append((neighbor, new_path))
        
        return None  # No path found
    
    def cleanup_expired(self, current_time: Optional[datetime] = None) -> int:
        """
        Clean up expired reservations and cooldowns.
        
        Args:
            current_time: Current game time
        
        Returns:
            Number of items cleaned up
        """
        current_time = current_time or datetime.now()
        cleaned = 0
        
        # Clean expired reservations
        expired_reservations = [
            prop_id for prop_id, res in self.reservations.items()
            if res.is_expired(current_time)
        ]
        for prop_id in expired_reservations:
            del self.reservations[prop_id]
            cleaned += 1
        
        # Clean expired cooldowns
        expired_cooldowns = [
            prop_id for prop_id, cd in self.cooldowns.items()
            if cd.is_ready(current_time)
        ]
        for prop_id in expired_cooldowns:
            del self.cooldowns[prop_id]
            cleaned += 1
        
        return cleaned
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the navigation system"""
        return {
            "active_reservations": len(self.reservations),
            "active_cooldowns": len(self.cooldowns),
            "navigation_nodes": len(self.navigation_graph),
            "reservations": {
                prop_id: {
                    "npc": res.npc_id,
                    "duration": res.duration,
                    "cooldown": res.cooldown,
                }
                for prop_id, res in self.reservations.items()
            },
        }
