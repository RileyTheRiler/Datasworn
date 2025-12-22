"""
DialogueShaper: Generates meta-instructions for NPC dialogue based on the player's archetype.
"""
from typing import TYPE_CHECKING, Optional
from src.narrative.archetype_types import ArchetypeProfile
from src.config.archetype_config_loader import ArchetypeConfigLoader

if TYPE_CHECKING:
    from src.director import DirectorPlan

class DialogueShaper:
    def __init__(self):
        self.config_loader = ArchetypeConfigLoader()

    def shape_dialogue(self, plan: 'DirectorPlan', profile: ArchetypeProfile) -> 'DirectorPlan':
        """
        Add dialogue guidance to the DirectorPlan based on archetype.
        
        Args:
            plan: The current plan.
            profile: The player's archetype profile.
        
        Returns:
            Updated DirectorPlan.
        """
        primary = profile.primary_archetype
        if not primary:
            return plan
            
        cluster = profile.get_cluster(primary)
        
        instruction = ""
        
        # General Cluster Guidance
        if cluster == "overcontrolled":
            instruction = "NPCs should sense the player's rigidity. Some may respect the discipline, others should challenge the lack of vulnerability."
        elif cluster == "undercontrolled":
            instruction = "NPCs should react to the player's volatility. Trust should be hard to earn. Use guarded language."
        elif cluster == "mixed":
            instruction = "NPCs should be confused by the player's inconsistencies. They may probe for the truth."
            
        if instruction:
            plan.notes_for_narrator = (plan.notes_for_narrator or "") + f"\n\n[DIALOGUE GUIDANCE]\n{instruction}"
            
        return plan
