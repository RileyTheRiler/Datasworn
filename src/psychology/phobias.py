"""
Phobia & Trigger System.

This module tracks specific irrational fears and manages the buildup of panic
when the character is exposed to those triggers.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Phobia:
    name: str # e.g., "Arachnophobia", "Claustrophobia"
    triggers: List[str] # ["spider", "web", "skitter"]
    severity: float # 0.0 to 1.0 (Impact on panic)
    accumulated_panic: float = 0.0 # Current buildup

@dataclass
class PhobiaSystem:
    """
    Manages phobias and panic responses.
    """
    active_phobias: Dict[str, Phobia] = field(default_factory=dict)
    
    def add_phobia(self, name: str, triggers: List[str], severity: float = 0.5):
        self.active_phobias[name] = Phobia(name, triggers, severity)
        
    def check_triggers(self, narrative_text: str) -> float:
        """
        Scan text for triggers and increase panic.
        Returns total panic increase.
        """
        text_lower = narrative_text.lower()
        total_increase = 0.0
        
        for phobia in self.active_phobias.values():
            triggered = False
            for trigger in phobia.triggers:
                if trigger in text_lower:
                    triggered = True
                    break
            
            if triggered:
                increase = phobia.severity * 0.2
                phobia.accumulated_panic = min(1.0, phobia.accumulated_panic + increase)
                total_increase += increase
                
        return total_increase

    def get_panic_status(self) -> Optional[str]:
        """
        Check if any phobia has triggered a panic attack.
        """
        for phobia in self.active_phobias.values():
            if phobia.accumulated_panic >= 1.0:
                return f"PANIC ATTACK: {phobia.name}"
                
        return None

    def decay_panic(self):
        """
        Reduce panic over time (call on scene advance).
        """
        for phobia in self.active_phobias.values():
            phobia.accumulated_panic = max(0.0, phobia.accumulated_panic - 0.1)

    def to_dict(self) -> dict:
        return {
            "active_phobias": {
                k: {
                    "name": v.name,
                    "triggers": v.triggers,
                    "severity": v.severity,
                    "accumulated_panic": v.accumulated_panic
                }
                for k, v in self.active_phobias.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PhobiaSystem":
        sys = cls()
        for k, v in data.get("active_phobias", {}).items():
            sys.active_phobias[k] = Phobia(
                name=v["name"],
                triggers=v["triggers"],
                severity=v["severity"],
                accumulated_panic=v.get("accumulated_panic", 0.0)
            )
        return sys
