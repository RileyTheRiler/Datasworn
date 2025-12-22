"""
Ship State Manager for The Exile Gambit.
Tracks dynamic changes to ship zones and systems based on narrative events.
"""

from typing import Dict, Any, List, Optional
from enum import Enum


class ZoneStatus(str, Enum):
    """Possible statuses for ship zones."""
    NORMAL = "normal"
    SEALED = "sealed"
    DAMAGED = "damaged"
    CRITICAL = "critical"
    OFFLINE = "offline"


class ShipEvent(str, Enum):
    """Events that can affect the ship's state."""
    MURDER_DISCOVERED = "murder_discovered"
    TENSION_RISES = "tension_rises"
    VIOLENCE_OCCURS = "violence_occurs"
    INVESTIGATION_STARTED = "investigation_started"
    KAI_SPIRALS = "kai_spirals"
    TRUST_BUILDS = "trust_builds"
    APPROACHING_PORT = "approaching_port"


class ShipStateManager:
    """
    Manages the dynamic state of The Exile Gambit.
    Tracks zone statuses, environmental changes, and pressure cooker mechanics.
    """
    
    def __init__(self):
        # Zone statuses: zone_id -> ZoneStatus
        self.zone_statuses: Dict[str, ZoneStatus] = {
            "bridge": ZoneStatus.NORMAL,
            "quarters_captain": ZoneStatus.SEALED,  # Sealed from start (murder)
            "engineering": ZoneStatus.NORMAL,
            "med_bay": ZoneStatus.NORMAL,
            "cargo_bay": ZoneStatus.NORMAL,
            "quarters_crew": ZoneStatus.NORMAL,
            "common_area": ZoneStatus.NORMAL,
            "observation_deck": ZoneStatus.NORMAL
        }
        
        # Pressure cooker metrics
        self.days_to_port: int = 8
        self.fuel_level: float = 1.0  # 0.0 to 1.0
        self.food_level: float = 1.0
        self.air_quality: float = 1.0
        
        # Environmental changes log
        self.changes_log: List[Dict[str, Any]] = []
        
        # Common area usage (tracks isolation vs community)
        self.common_area_usage: float = 0.5  # 0.0 (isolated) to 1.0 (community)
    
    def apply_event(self, event: ShipEvent, scene: int = 0) -> List[str]:
        """
        Apply a narrative event to the ship state.
        
        Args:
            event: The event that occurred
            scene: Current scene number
        
        Returns:
            List of environmental changes (descriptions for narrator)
        """
        changes = []
        
        if event == ShipEvent.MURDER_DISCOVERED:
            if self.zone_statuses["quarters_captain"] != ZoneStatus.SEALED:
                self.zone_statuses["quarters_captain"] = ZoneStatus.SEALED
                changes.append("Captain's quarters sealed with improvised barrier")
                self._log_change(scene, "quarters_captain", "sealed", "Murder investigation")
        
        elif event == ShipEvent.TENSION_RISES:
            self.common_area_usage = max(0.0, self.common_area_usage - 0.2)
            changes.append("Common area less used; crew isolates")
            self._log_change(scene, "common_area", "less_used", "Rising tension")
        
        elif event == ShipEvent.VIOLENCE_OCCURS:
            # Random zone shows signs of violence
            affected_zones = ["common_area", "quarters_crew", "cargo_bay"]
            import random
            zone = random.choice(affected_zones)
            changes.append(f"Blood stains, damaged equipment in {zone}")
            self._log_change(scene, zone, "damaged", "Violence occurred")
        
        elif event == ShipEvent.INVESTIGATION_STARTED:
            changes.append("Quarters show signs of search")
            self._log_change(scene, "quarters_crew", "searched", "Investigation")
        
        elif event == ShipEvent.KAI_SPIRALS:
            self.zone_statuses["engineering"] = ZoneStatus.DAMAGED
            self.fuel_level = max(0.0, self.fuel_level - 0.1)
            changes.append("Engineering becomes more chaotic; systems start failing")
            self._log_change(scene, "engineering", "damaged", "Kai's spiral")
        
        elif event == ShipEvent.TRUST_BUILDS:
            self.common_area_usage = min(1.0, self.common_area_usage + 0.2)
            changes.append("Common area shows more use; personal items shared")
            self._log_change(scene, "common_area", "more_used", "Trust building")
        
        elif event == ShipEvent.APPROACHING_PORT:
            changes.append("Packing begins; impermanence visible")
            self._log_change(scene, "quarters_crew", "packing", "Approaching port")
        
        return changes
    
    def advance_day(self) -> Dict[str, Any]:
        """
        Advance the ship's timeline by one day.
        Updates pressure cooker metrics.
        
        Returns:
            Dict with status updates
        """
        self.days_to_port = max(0, self.days_to_port - 1)
        
        # Resources deplete
        self.fuel_level = max(0.0, self.fuel_level - 0.05)
        self.food_level = max(0.0, self.food_level - 0.08)
        self.air_quality = max(0.0, self.air_quality - 0.02)
        
        return {
            "days_to_port": self.days_to_port,
            "fuel_level": self.fuel_level,
            "food_level": self.food_level,
            "air_quality": self.air_quality,
            "pressure_level": self._calculate_pressure()
        }
    
    def _calculate_pressure(self) -> float:
        """Calculate overall pressure level (0.0 to 1.0)."""
        # Pressure increases as resources deplete and time runs out
        time_pressure = 1.0 - (self.days_to_port / 8.0)
        resource_pressure = 1.0 - ((self.fuel_level + self.food_level + self.air_quality) / 3.0)
        isolation_pressure = 1.0 - self.common_area_usage
        
        return (time_pressure + resource_pressure + isolation_pressure) / 3.0
    
    def get_zone_status(self, zone_id: str) -> ZoneStatus:
        """Get the current status of a zone."""
        return self.zone_statuses.get(zone_id, ZoneStatus.NORMAL)
    
    def set_zone_status(self, zone_id: str, status: ZoneStatus, reason: str = "", scene: int = 0):
        """Manually set a zone's status."""
        if zone_id in self.zone_statuses:
            old_status = self.zone_statuses[zone_id]
            self.zone_statuses[zone_id] = status
            self._log_change(scene, zone_id, status.value, reason)
    
    def _log_change(self, scene: int, zone_id: str, change_type: str, reason: str):
        """Log an environmental change."""
        self.changes_log.append({
            "scene": scene,
            "zone_id": zone_id,
            "change_type": change_type,
            "reason": reason
        })
    
    def get_pressure_description(self) -> str:
        """Get a narrative description of the current pressure level."""
        pressure = self._calculate_pressure()
        
        if pressure < 0.2:
            return "The ship feels stable. Routine operations."
        elif pressure < 0.4:
            return "Tension is building. Small irritations magnified."
        elif pressure < 0.6:
            return "The air feels thick. Everyone is on edge."
        elif pressure < 0.8:
            return "Pressure cooker. One spark could ignite everything."
        else:
            return "Critical. The ship is a powder keg."
    
    def get_narrator_context(self) -> str:
        """Generate context for the narrator about ship state."""
        lines = ["[SHIP STATE CONTEXT]", ""]
        lines.append(f"Days to port: {self.days_to_port}")
        lines.append(f"Pressure level: {self.get_pressure_description()}")
        lines.append("")
        lines.append("Zone Statuses:")
        
        for zone_id, status in self.zone_statuses.items():
            if status != ZoneStatus.NORMAL:
                lines.append(f"  - {zone_id}: {status.value}")
        
        lines.append("")
        lines.append(f"Fuel: {int(self.fuel_level * 100)}%")
        lines.append(f"Food: {int(self.food_level * 100)}%")
        lines.append(f"Air Quality: {int(self.air_quality * 100)}%")
        lines.append(f"Community vs Isolation: {int(self.common_area_usage * 100)}% community")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for game state storage."""
        return {
            "zone_statuses": {k: v.value for k, v in self.zone_statuses.items()},
            "days_to_port": self.days_to_port,
            "fuel_level": self.fuel_level,
            "food_level": self.food_level,
            "air_quality": self.air_quality,
            "common_area_usage": self.common_area_usage,
            "changes_log": self.changes_log
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShipStateManager":
        """Deserialize from game state."""
        manager = cls()
        
        # Restore zone statuses
        zone_statuses_data = data.get("zone_statuses", {})
        for zone_id, status_str in zone_statuses_data.items():
            manager.zone_statuses[zone_id] = ZoneStatus(status_str)
        
        # Restore metrics
        manager.days_to_port = data.get("days_to_port", 8)
        manager.fuel_level = data.get("fuel_level", 1.0)
        manager.food_level = data.get("food_level", 1.0)
        manager.air_quality = data.get("air_quality", 1.0)
        manager.common_area_usage = data.get("common_area_usage", 0.5)
        manager.changes_log = data.get("changes_log", [])
        
        return manager
