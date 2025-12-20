"""
Ending Preparation System.

This module tracks the state of the narrative to determine when a conclusion
is viable and what kind of ending tone is appropriate.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

class EndingType(Enum):
    TRIUMPH = "TRIUMPH"        # High resources, solved mysteries, good relationships
    TRAGEDY = "TRAGEDY"        # Low resources, unresolved threads, broken bonds
    BITTERSWEET = "BITTERSWEET" # Mixed bag

@dataclass
class EndingPreparationSystem:
    """
    Monitors narrative completion state.
    """
    
    def check_finale_readiness(self, 
                             active_plots: int,
                             resolved_plots: int, 
                             unresolved_mysteries: int,
                             scene_count: int) -> float:
        """
        Calculate a readiness score (0.0 to 1.0) for the finale.
        """
        if scene_count < 20: 
            return 0.0 # Too early
            
        # We need significant resolution
        total_plots = active_plots + resolved_plots
        if total_plots == 0:
            return 0.5 # Default middle ground if no plots tracked
            
        resolution_ratio = resolved_plots / total_plots
        
        # Penalize for dangling mysteries
        mystery_penalty = min(0.3, unresolved_mysteries * 0.1)
        
        score = resolution_ratio - mystery_penalty
        
        # Boost if scene count is very high (force ending)
        if scene_count > 50:
            score += 0.4
            
        return max(0.0, min(1.0, score))

    def suggest_ending_flavor(self, 
                            reputation_score: int, # -100 to 100
                            avg_bond_strength: float # 0 to 100
                            ) -> EndingType:
        """
        Suggest the tone of the ending based on player's journey.
        """
        score = reputation_score + avg_bond_strength
        
        if score > 80:
            return EndingType.TRIUMPH
        elif score < -20:
            return EndingType.TRAGEDY
        else:
            return EndingType.BITTERSWEET

    def to_dict(self) -> dict:
        return {} # Stateless calculation engine for now, or could store 'locked_ending'

    @classmethod
    def from_dict(cls, data: dict) -> "EndingPreparationSystem":
        return cls()
