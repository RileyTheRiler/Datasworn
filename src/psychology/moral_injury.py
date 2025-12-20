"""
Moral Injury System.

This module tracks psychological damage from violating one's own moral code,
such as killing defenseless enemies, betraying allies, or failing to act.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class TransgressionType(str, Enum):
    KILLING = "killing"             # Killed someone unnecessarily
    BETRAYAL = "betrayal"           # Broke trust with an ally
    COWARDICE = "cowardice"         # Failed to act when action was needed
    CRUELTY = "cruelty"             # Caused unnecessary suffering
    THEFT = "theft"                 # Took what wasn't yours
    DECEPTION = "deception"         # Lied to gain advantage

@dataclass
class Transgression:
    type: TransgressionType
    description: str
    guilt_weight: float = 0.2  # Impact on overall guilt level
    processed: bool = False    # Has this been "worked through"?

@dataclass
class MoralInjurySystem:
    """
    Tracks accumulated moral damage.
    """
    transgressions: List[Transgression] = field(default_factory=list)
    total_guilt: float = 0.0
    
    def record_transgression(self, t_type: TransgressionType, description: str, weight: float = 0.2):
        """
        Record a moral violation.
        """
        trans = Transgression(t_type, description, weight)
        self.transgressions.append(trans)
        self.total_guilt = min(1.0, self.total_guilt + weight)
        
    def get_guilt_context(self) -> Optional[str]:
        """
        Generate narrator guidance based on guilt level.
        """
        if self.total_guilt >= 0.8:
            return "[HEAVY GUILT: The character is consumed by remorse. Describe haunted eyes, hesitation, and self-loathing.]"
        elif self.total_guilt >= 0.5:
            return "[MODERATE GUILT: The character is troubled. They second-guess their actions and avoid eye contact.]"
        elif self.total_guilt >= 0.2:
            return "[MILD GUILT: A faint unease lingers. The character occasionally stares at nothing.]"
        return None
    
    def process_transgression(self, index: int) -> bool:
        """
        Mark a transgression as processed (e.g., through confession or therapy).
        Reduces guilt slightly.
        """
        if 0 <= index < len(self.transgressions):
            t = self.transgressions[index]
            if not t.processed:
                t.processed = True
                self.total_guilt = max(0.0, self.total_guilt - t.guilt_weight * 0.5)
                return True
        return False

    def to_dict(self) -> dict:
        return {
            "transgressions": [
                {
                    "type": t.type.value,
                    "description": t.description,
                    "guilt_weight": t.guilt_weight,
                    "processed": t.processed
                }
                for t in self.transgressions
            ],
            "total_guilt": self.total_guilt
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MoralInjurySystem":
        sys = cls()
        sys.total_guilt = data.get("total_guilt", 0.0)
        for t in data.get("transgressions", []):
            sys.transgressions.append(Transgression(
                type=TransgressionType(t["type"]),
                description=t["description"],
                guilt_weight=t["guilt_weight"],
                processed=t.get("processed", False)
            ))
        return sys
