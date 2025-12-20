"""
Opening Hook System.

This module provides a structured "hook architecture" for campaign openings,
ensuring players are immediately invested through a 3-scene escalation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import random

@dataclass
class SceneTemplate:
    """Template for a generated scene."""
    scene_type: str  # NORMAL_WORLD, INCITING_INCIDENT, POINT_OF_NO_RETURN
    description: str
    focus: str
    suggested_action: str
    
@dataclass
class OpeningHookSystem:
    """
    Generates structured 3-scene intros.
    """
    
    def generate_opening_sequence(self, campaign_truths: Dict[str, str], 
                                 character_role: str, 
                                 character_goal: str) -> List[SceneTemplate]:
        """
        Creates first 3 scenes with escalating tension and personal stakes.
        """
        return [
            self._create_normal_world(character_role, character_goal),
            self._create_inciting_incident(campaign_truths),
            self._create_point_of_no_return(character_goal)
        ]

    def _create_normal_world(self, role: str, goal: str) -> SceneTemplate:
        """
        Scene 1: Establish routine and context.
        """
        templates = [
            f"You are performing your duties as a {role}. It's a quiet shift.",
            f"The local settlement relies on you as a {role}. People are going about their daily business.",
            f"You are reviewing your plans to {goal}. Everything seems to be in order."
        ]
        
        return SceneTemplate(
            scene_type="NORMAL_WORLD",
            description=random.choice(templates),
            focus="Establish character baseline and setting atmosphere.",
            suggested_action="Interact with a friendly NPC or perform a routine check."
        )

    def _create_inciting_incident(self, truths: Dict[str, str]) -> SceneTemplate:
        """
        Scene 2: Disruption of the status quo.
        """
        # Incorporate truths if possible, otherwise generic sci-fi tropes
        catalyst = "A distress signal is received."
        if "ironsworn" in truths:
             catalyst = "An Ironsworn arrives with grave news."
        elif "precursor" in truths:
             catalyst = "A precursor artifact activates unexpectedly."
             
        return SceneTemplate(
            scene_type="INCITING_INCIDENT",
            description=f"Suddenly, the calm is broken. {catalyst} Alarms begin to blare.",
            focus="Introduce the immediate threat or mystery.",
            suggested_action="Investigate the disturbance or secure the area."
        )

    def _create_point_of_no_return(self, goal: str) -> SceneTemplate:
        """
        Scene 3: Forced choice or irreversible event.
        """
        return SceneTemplate(
            scene_type="POINT_OF_NO_RETURN",
            description=f"The situation escalates. You cannot go back to your old life. To pursue {goal}, you must leave now.",
            focus="Force a commitment to the adventure.",
            suggested_action="Make a vow or leave the safe zone."
        )
