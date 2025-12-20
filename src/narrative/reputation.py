"""
Moral Reputation System.

This module tracks the moral alignment of the player based on their choices,
allowing the world to react to their reputation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class ReputationScore:
    """Score on a specific moral axis (-100 to 100)."""
    value: int = 0
    
    # Axis definitions
    # Merciful (+) | Ruthless (-)
    # Honest (+)   | Deceptive (-)
    # Selfless (+) | Selfish (-)

    def adjust(self, amount: int):
        self.value = max(-100, min(100, self.value + amount))

    @property
    def label(self) -> str:
        if self.value > 50: return "HIGH_POSITIVE"
        if self.value < -50: return "HIGH_NEGATIVE"
        if self.value > 10: return "LEANING_POSITIVE"
        if self.value < -10: return "LEANING_NEGATIVE"
        return "NEUTRAL"

@dataclass
class MoralReputationSystem:
    """
    Tracks player reputation across different axes.
    """
    mercy_ruthless: ReputationScore = field(default_factory=ReputationScore)
    honest_deceptive: ReputationScore = field(default_factory=ReputationScore)
    selfless_selfish: ReputationScore = field(default_factory=ReputationScore)
    
    history: List[str] = field(default_factory=list) # Log of moral choices
    
    def record_choice(self, description: str, 
                     mercy_delta: int = 0, 
                     honest_delta: int = 0, 
                     selfless_delta: int = 0):
        """
        Record a choice that impacts reputation.
        """
        self.mercy_ruthless.adjust(mercy_delta)
        self.honest_deceptive.adjust(honest_delta)
        self.selfless_selfish.adjust(selfless_delta)
        
        self.history.append(description)

    def get_reputation_summary(self) -> str:
        """
        Get a description of how the world sees the player.
        """
        traits = []
        
        if self.mercy_ruthless.value > 50: traits.append("Known as a merciful protector.")
        elif self.mercy_ruthless.value < -50: traits.append("Feared as a ruthless executioner.")
        
        if self.honest_deceptive.value > 50: traits.append("Trusted to keep their word.")
        elif self.honest_deceptive.value < -50: traits.append("Suspected of being a liar.")
        
        if self.selfless_selfish.value > 50: traits.append("Praised for their generosity.")
        elif self.selfless_selfish.value < -50: traits.append("Despised for their greed.")
        
        if not traits:
            return "An unknown wanderer with no reputation yet."
            
        return " ".join(traits)

    def to_dict(self) -> dict:
        return {
            "mercy_ruthless": self.mercy_ruthless.value,
            "honest_deceptive": self.honest_deceptive.value,
            "selfless_selfish": self.selfless_selfish.value,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MoralReputationSystem":
        system = cls()
        system.mercy_ruthless.value = data.get("mercy_ruthless", 0)
        system.honest_deceptive.value = data.get("honest_deceptive", 0)
        system.selfless_selfish.value = data.get("selfless_selfish", 0)
        system.history = data.get("history", [])
        return system
