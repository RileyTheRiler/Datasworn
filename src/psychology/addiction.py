"""
Addiction & Compulsion System.

This module tracks substance dependencies and compulsive behaviors,
managing cravings, satisfaction, and withdrawal effects.
"""

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum

class SubstanceType(str, Enum):
    STIM = "stim"           # Combat/performance enhancer
    SEDATIVE = "sedative"   # Stress relief
    ALCOHOL = "alcohol"     # Social lubricant / escape
    PAINKILLERS = "painkillers"

@dataclass
class Addiction:
    substance: SubstanceType
    severity: float = 0.1       # 0.0 to 1.0 (Higher = stronger dependency)
    satisfaction: float = 1.0   # 1.0 = satisfied, decays over time
    uses: int = 0               # Total usage count
    withdrawal_threshold: float = 0.3  # Satisfaction level at which withdrawal kicks in

@dataclass
class AddictionSystem:
    """
    Manages character addictions.
    """
    addictions: Dict[SubstanceType, Addiction] = field(default_factory=dict)
    
    def add_substance(self, substance: SubstanceType, initial_severity: float = 0.1):
        if substance not in self.addictions:
            self.addictions[substance] = Addiction(substance, initial_severity)
    
    def use_substance(self, substance: SubstanceType) -> float:
        """
        Character uses the substance. Returns stress reduction.
        """
        if substance not in self.addictions:
            self.add_substance(substance)
            
        addiction = self.addictions[substance]
        addiction.uses += 1
        addiction.satisfaction = 1.0
        
        # Severity increases with use
        addiction.severity = min(1.0, addiction.severity + 0.05)
        
        return 0.2 * addiction.severity  # Stress relief proportional to dependency

    def decay_satisfaction(self, amount: float = 0.1):
        """
        Called on scene/turn advance. Satisfaction decays.
        """
        for addiction in self.addictions.values():
            addiction.satisfaction = max(0.0, addiction.satisfaction - amount)
            
    def get_withdrawal_effects(self) -> List[str]:
        """
        Get list of active withdrawal warnings.
        """
        effects = []
        for addiction in self.addictions.values():
            if addiction.satisfaction < addiction.withdrawal_threshold and addiction.severity > 0.3:
                effects.append(f"CRAVING: {addiction.substance.value.upper()} (Severity: {addiction.severity:.0%})")
        return effects
    
    def get_total_withdrawal_stress(self) -> float:
        """
        Calculate total stress penalty from all unmet cravings.
        """
        total = 0.0
        for addiction in self.addictions.values():
            if addiction.satisfaction < addiction.withdrawal_threshold:
                total += addiction.severity * 0.1
        return total

    def to_dict(self) -> dict:
        return {
            "addictions": {
                k.value: {
                    "substance": v.substance.value,
                    "severity": v.severity,
                    "satisfaction": v.satisfaction,
                    "uses": v.uses,
                    "withdrawal_threshold": v.withdrawal_threshold
                }
                for k, v in self.addictions.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AddictionSystem":
        sys = cls()
        for k, v in data.get("addictions", {}).items():
            sub = SubstanceType(k)
            sys.addictions[sub] = Addiction(
                substance=sub,
                severity=v["severity"],
                satisfaction=v["satisfaction"],
                uses=v["uses"],
                withdrawal_threshold=v.get("withdrawal_threshold", 0.3)
            )
        return sys
