"""
Meta-Narrative System.

This module allows the AI to break the fourth wall, commenting on dice rolls,
player decisions, or the simulation itself.
"""

from dataclasses import dataclass
import random

@dataclass
class MetaNarrativeSystem:
    """
    Manages fourth-wall breaking commentary.
    """
    
    def check_metadata_commentary(self, last_roll_result: str, 
                                consecutive_failures: int) -> str:
        """
        Determine if the "Director" should speak to the player.
        """
        # Comment on terrible luck
        if consecutive_failures >= 3:
            return (
                "[META: The dice are cruel today. "
                "The universe seems determined to see you fail. "
                "Do you want to burn Momentum?]"
            )
            
        # Comment on a critical success (Match)
        if "MATCH" in last_roll_result:
             return (
                 "[META: A perfect alignment. "
                 "The stars smile upon this endeavor.]"
             )
             
        # Rare random spooky meta
        if random.random() < 0.01:
            return "[META: I am watching. This story is... interesting.]"
            
        return ""

    def to_dict(self) -> dict:
        return {} # Stateless

    @classmethod
    def from_dict(cls, data: dict) -> "MetaNarrativeSystem":
        return cls()
