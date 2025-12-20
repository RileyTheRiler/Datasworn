"""
Environmental Hazards System for Starforged AI Game Master.

Manages space hazards, weather effects, and their impact on gameplay.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import random


# ============================================================================
# Enums
# ============================================================================

class HazardType(Enum):
    """Types of environmental hazards."""
    RADIATION_STORM = "radiation_storm"
    SOLAR_FLARE = "solar_flare"
    ASTEROID_FIELD = "asteroid_field"
    GRAVITY_WELL = "gravity_well"
    ION_STORM = "ion_storm"
    CORROSIVE_ATMOSPHERE = "corrosive_atmosphere"
    EXTREME_COLD = "extreme_cold"
    EXTREME_HEAT = "extreme_heat"
    PSI_STORM = "psi_storm"  # Precursor/mystic related


class HazardSeverity(Enum):
    """Severity levels for hazards."""
    MINOR = "minor"         # Cosmetic or slight inconvenience
    MODERATE = "moderate"   # Requires checks or resource cost
    DANGEROUS = "dangerous" # Significant damage risk
    EXTREME = "extreme"     # Fatal without protection


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Hazard:
    """An active environmental hazard."""
    name: str
    hazard_type: HazardType
    severity: HazardSeverity
    description: str
    effect_description: str
    duration_scenes: int = 1  # How long it lasts
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hazard_type": self.hazard_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "effect_description": self.effect_description,
            "duration_scenes": self.duration_scenes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hazard":
        return cls(
            name=data["name"],
            hazard_type=HazardType(data["hazard_type"]),
            severity=HazardSeverity(data["severity"]),
            description=data["description"],
            effect_description=data["effect_description"],
            duration_scenes=data.get("duration_scenes", 1)
        )


# ============================================================================
# Hazard Generator
# ============================================================================

class HazardGenerator:
    """Generates procedural hazards based on location and context."""
    
    def generate_travel_hazard(self, system_type: str = "yellow_star") -> Optional[Hazard]:
        """
        Generate a hazard that might be encountered during travel.
        Returns None if travel is safe (most of the time).
        """
        # Base chance of hazard is 20%
        if random.random() > 0.2:
            return None
            
        hazard_type = random.choice(list(HazardType))
        severity = random.choice(list(HazardSeverity))
        
        # Customize based on system type context would go here
        
        templates = {
            HazardType.RADIATION_STORM: ("Radiation Storm", "Sensors are blinded by intense radiation."),
            HazardType.SOLAR_FLARE: ("Solar Flare", "A massive ejection from the local star threatens the ship."),
            HazardType.ASTEROID_FIELD: ("Dense Asteroid Field", "Thousands of rocks drift in the travel lane."),
            HazardType.ION_STORM: ("Ion Storm", "Electrical discharges arc across the hull."),
        }
        
        name, desc = templates.get(hazard_type, ("Unknown Anomaly", "Something strange is happening."))
        
        return Hazard(
            name=name,
            hazard_type=hazard_type,
            severity=severity,
            description=desc,
            effect_description=f"Causes {severity.value} impact on ship systems.",
            duration_scenes=random.randint(1, 3)
        )
