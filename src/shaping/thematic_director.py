"""
ThematicDirector: Influences narrative pacing, tone, and direction based on the player's archetype.
"""
from typing import TYPE_CHECKING, Optional, Any
from src.narrative.archetype_types import ArchetypeProfile
from src.config.archetype_config_loader import ArchetypeConfigLoader

if TYPE_CHECKING:
    from src.director import DirectorPlan, Pacing, Tone

class ThematicDirector:
    def __init__(self):
        self.config_loader = ArchetypeConfigLoader()

    def apply_archetype_influence(self, plan: 'DirectorPlan', profile: ArchetypeProfile) -> 'DirectorPlan':
        """
        Adjust the DirectorPlan based on the player's archetype profile.
        
        Args:
            plan: The initial DirectorPlan (from heuristics or LLM).
            profile: The player's current ArchetypeProfile.
            
        Returns:
            Review DirectorPlan with thematic adjustments.
        """
        if not profile.primary_archetype:
            return plan

        primary = profile.primary_archetype
        confidence = profile.confidence
        
        # 1. Add Thematic Guidance Notes
        archetype_def = self.config_loader.get_archetype(primary)
        if archetype_def:
            note = f"\n[THEMATIC INFLUENCE: {primary.upper()}]"
            note += f"\nPsychological Need: {archetype_def.psychological_need}"
            note += f"\nMoral Need: {archetype_def.moral_need}"
            
            # Advice based on confidence
            if confidence > 0.6:
                note += "\nThe archetype is strong. Challenge their worldview directly."
            else:
                note += "\nThe archetype is emerging. Feed their need to encourage expression."
            
            # Map Cluster to Pacing/Tone tendencies
            # This is hardcoded for now as it's not in the config explicitly, 
            # but derived from the nature of the clusters.
            cluster = profile.get_cluster(primary)
            
            # 2. Influence Tone/Pacing (Soft Influence)
            # We don't override strongly unless the Director didn't have a strong opinion,
            # but we append guidance.
            if cluster == "overcontrolled":
                note += "\nAtmosphere: Oppressive, rigid, structured. High stakes for failure."
            elif cluster == "undercontrolled":
                note += "\nAtmosphere: Chaotic, visceral, unpredictable. Emotional volatility."
            
            plan.notes_for_narrator = (plan.notes_for_narrator or "") + note

        return plan
