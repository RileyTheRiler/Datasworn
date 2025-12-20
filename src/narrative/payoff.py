"""
Narrative Payoff Tracker System.

This module implements the 'Chekhov's Gun' principle by tracking foreshadowed
elements (seeds) and ensuring they pay off within a reasonable narrative timeframe.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import uuid

@dataclass
class PayoffSeed:
    """A single foreshadowed element that needs resolution."""
    seed_id: str
    seed_type: str  # MYSTERY, THREAT, RELATIONSHIP, ARTIFACT, PROPHECY
    description: str
    planted_scene: int
    must_resolve_by: int
    resolved: bool = False
    hints_given: int = 0
    resolution_scene: Optional[int] = None
    outcome: str = ""

@dataclass
class PayoffTracker:
    """
    Tracks narrative promises and ensures they are kept.
    
    Attributes:
        planted_seeds: Dictionary mapping seed_id to PayoffSeed objects.
        payoff_types: List of valid seed types.
    """
    planted_seeds: Dict[str, PayoffSeed] = field(default_factory=dict)
    
    PAYOFF_TYPES = ["MYSTERY", "THREAT", "RELATIONSHIP", "ARTIFACT", "PROPHECY"]

    def plant_seed(self, seed_type: str, description: str, current_scene: int, max_scenes_until_payoff: int = 10) -> str:
        """
        Track a foreshadowed element that MUST be resolved.
        
        Args:
            seed_type: Category of the seed (must be in PAYOFF_TYPES).
            description: Narrative description of what was foreshadowed.
            current_scene: The scene number where this was planted.
            max_scenes_until_payoff: How many scenes can pass before this must resolve.
            
        Returns:
            The unique ID of the planted seed.
        """
        if seed_type not in self.PAYOFF_TYPES:
             # Default to MYSTERY if invalid type, or could raise ValueError
             seed_type = "MYSTERY"

        seed_id = str(uuid.uuid4())
        seed = PayoffSeed(
            seed_id=seed_id,
            seed_type=seed_type,
            description=description,
            planted_scene=current_scene,
            must_resolve_by=current_scene + max_scenes_until_payoff,
        )
        self.planted_seeds[seed_id] = seed
        return seed_id

    def resolve_seed(self, seed_id: str, current_scene: int, outcome: str) -> bool:
        """
        Mark a seed as resolved.
        
        Args:
            seed_id: The ID of the seed to resolve.
            current_scene: The scene number where resolution happened.
            outcome: Description of how it was resolved.
            
        Returns:
            True if successfully resolved, False if seed not found.
        """
        if seed_id in self.planted_seeds:
            self.planted_seeds[seed_id].resolved = True
            self.planted_seeds[seed_id].resolution_scene = current_scene
            self.planted_seeds[seed_id].outcome = outcome
            return True
        return False

    def get_overdue_seeds(self, current_scene: int, warning_threshold: int = 2) -> List[PayoffSeed]:
        """
        Return seeds that need resolution SOON or are already overdue.
        
        Args:
            current_scene: Current scene number.
            warning_threshold: Warn if within this many scenes of deadline.
            
        Returns:
            List of PayoffSeed objects that are unresolved and pressing.
        """
        overdue = []
        for seed in self.planted_seeds.values():
            if not seed.resolved:
                # Check if we are close to or past the deadline
                if current_scene >= (seed.must_resolve_by - warning_threshold):
                    overdue.append(seed)
        return overdue

    def get_active_seeds(self) -> List[PayoffSeed]:
        """Return all currently unresolved seeds."""
        return [s for s in self.planted_seeds.values() if not s.resolved]

    def to_dict(self) -> dict:
        """Serialize state."""
        return {
            "planted_seeds": {
                sid: {
                    "seed_id": s.seed_id,
                    "seed_type": s.seed_type,
                    "description": s.description,
                    "planted_scene": s.planted_scene,
                    "must_resolve_by": s.must_resolve_by,
                    "resolved": s.resolved,
                    "hints_given": s.hints_given,
                    "resolution_scene": s.resolution_scene,
                    "outcome": s.outcome
                }
                for sid, s in self.planted_seeds.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PayoffTracker":
        """Deserialize state."""
        tracker = cls()
        seeds_data = data.get("planted_seeds", {})
        for sid, s_data in seeds_data.items():
            tracker.planted_seeds[sid] = PayoffSeed(**s_data)
        return tracker
