"""
Environmental Storyteller.

This module enhances scene descriptions by generating sensory details and
atmospheric elements that imply history and mood.
"""

from dataclasses import dataclass
from typing import List, Optional
import random

@dataclass
class EnvironmentalStoryteller:
    """
    Generates sensory details for scenes.
    """
    
    def generate_atmosphere(self, location_type: str, mood: str) -> str:
        """
        Get a sensory description based on location and mood.
        """
        # In a real implementation, this would query an LLM or a large database
        # For now, we use a small curated list for demonstration
        
        details = []
        
        if "ruin" in location_type.lower() or "derelict" in location_type.lower():
            details.extend([
                "The air tastes of copper and stale dust.",
                "Wires hang from the ceiling like weeping willow branches.",
                "A child's toy sits untouched in the corner, gathering grime.",
                "The only sound is the rhythmic dripping of a leaking pipe."
            ])
        elif "station" in location_type.lower() or "city" in location_type.lower():
            details.extend([
                "The hum of ventilation fans is a constant, low-frequency pressure.",
                "Neon lights reflect off puddles of synthetic oil.",
                "The smell of ozone and street food hangs in the air.",
                "Holographic ads flicker, glitching into static occasionally."
            ])
        elif "wild" in location_type.lower() or "planet" in location_type.lower():
            details.extend([
                "The wind carries the scent of sulfur and strange pollen.",
                "Vegetation curls away from your touch, reacting to heat.",
                "The ground vibrates slightly, as if something massive moves below.",
                "Strange avian cries echo from the canopy."
            ])
            
        if not details:
            details = ["The area is quiet, waiting for something to happen."]
            
        # Select one or two details
        selected = random.sample(details, min(2, len(details)))
        return " ".join(selected)

    def to_dict(self) -> dict:
        return {} 

    @classmethod
    def from_dict(cls, data: dict) -> "EnvironmentalStoryteller":
        return cls()
