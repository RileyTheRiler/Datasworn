"""
SeedPlanter: Selects and manages archetype-specific foreshadowing seeds.
"""
from typing import TYPE_CHECKING, List, Optional
import random
from src.narrative.archetype_types import ArchetypeProfile
from src.config.archetype_config_loader import ArchetypeConfigLoader

if TYPE_CHECKING:
    from src.director import DirectorPlan, DirectorState

class SeedPlanter:
    def __init__(self):
        self.config_loader = ArchetypeConfigLoader()

    def plant_seeds(self, plan: 'DirectorPlan', profile: ArchetypeProfile, state: 'DirectorState') -> 'DirectorPlan':
        """
        Inject foreshadowing seeds into the DirectorPlan based on the archetype.
        
        Args:
            plan: The current plan.
            profile: Evidence-based archetype profile.
            state: Director state (to track what has been foreshadowed).
            
        Returns:
            Updated DirectorPlan with possible foreshadowing instructions.
        """
        primary = profile.primary_archetype
        if not primary or primary == 'unknown':
            return plan
            
        # Helper to get seeds
        try:
            seeds = self.config_loader.get_seeds(primary)
        except ValueError:
            return plan # Archetype not found
            
        if not seeds:
            return plan
            
        # Chance to plant a seed (higher if confidence is high)
        chance = 0.3 + (profile.confidence * 0.4) 
        
        if random.random() < chance:
            seed_text = random.choice(seeds)
            
            # Add to DirectorState for tracking
            # Format: "[ARCHETYPE] Seed text"
            seed_tracking_str = f"[{primary.upper()}] {seed_text}"
            
            # Avoid exact duplicates in recent history
            # DirectorState.foreshadowing is List[str]
            if seed_tracking_str not in state.foreshadowing:
                state.foreshadowing.append(seed_tracking_str)
                if len(state.foreshadowing) > 10:
                    state.foreshadowing.pop(0)
                    
                # Add to Plan
                plan.notes_for_narrator = (plan.notes_for_narrator or "") + f"\n\n[FORESHADOWING]\nIncorporate this detail: {seed_text}"
        
        return plan
