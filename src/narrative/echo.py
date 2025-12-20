"""
Choice Echo System.

This module ensures that past player choices are remembered by the world
and its inhabitants, preventing "amnesia" about significant actions.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import random

@dataclass
class SignificantChoice:
    """A choice made by the player that should be remembered."""
    choice_id: str
    description: str
    scene: int
    witnesses: List[str]  # NPC IDs who saw it/know about it
    tags: List[str] = field(default_factory=list) # e.g. ["violent", "merciful", "selfish"]
    mentioned_count: int = 0
    outcome: str = ""

@dataclass
class ChoiceEchoSystem:
    """
    Manages the history of significant choices and retrieves them for callbacks.
    """
    history: List[SignificantChoice] = field(default_factory=list)
    
    def record_choice(self, choice_id: str, description: str, current_scene: int, 
                     witnesses: List[str], tags: List[str] = None) -> None:
        """
        Log a significant choice.
        """
        self.history.append(SignificantChoice(
            choice_id=choice_id,
            description=description,
            scene=current_scene,
            witnesses=witnesses,
            tags=tags or []
        ))

    def get_recallable_choices(self, npc_id: str, current_scene: int, 
                              context_tags: List[str] = None) -> List[SignificantChoice]:
        """
        Find choices this NPC knows about and might bring up.
        """
        relevant = []
        for choice in self.history:
            # 1. NPC must be a witness
            if npc_id in choice.witnesses:
                # 2. Choice shouldn't be brand new (give it at least 1 scene)
                if current_scene > choice.scene:
                    # 3. If context tags provided, prioritize matches
                    if context_tags:
                        if any(tag in choice.tags for tag in context_tags):
                            relevant.append(choice)
                    else:
                        relevant.append(choice)
        return relevant

    def generate_echo(self, npc_id: str, current_scene: int, context: str = "") -> Optional[str]:
        """
        Generate a dialogue line where NPC references a past choice.
        """
        # Simple tag matching based on context
        tags = []
        if "combat" in context:
            tags = ["violent", "brave"]
        elif "negotiation" in context:
            tags = ["merciful", "deceptive"]
            
        candidates = self.get_recallable_choices(npc_id, current_scene, tags)
        
        if candidates:
            # Prefer choices mentioned less often
            candidates.sort(key=lambda x: x.mentioned_count)
            choice = candidates[0]
            
            choice.mentioned_count += 1
            return f"I remember what you did back in scene {choice.scene}. {choice.description}."
            
        return None

    def to_dict(self) -> dict:
        """Serialize state."""
        return {
            "history": [
                {
                    "choice_id": c.choice_id,
                    "description": c.description,
                    "scene": c.scene,
                    "witnesses": c.witnesses,
                    "tags": c.tags,
                    "mentioned_count": c.mentioned_count,
                    "outcome": c.outcome
                }
                for c in self.history
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChoiceEchoSystem":
        """Deserialize state."""
        system = cls()
        for c_data in data.get("history", []):
            system.history.append(SignificantChoice(
                choice_id=c_data["choice_id"],
                description=c_data["description"],
                scene=c_data["scene"],
                witnesses=c_data.get("witnesses", []),
                tags=c_data.get("tags", []),
                mentioned_count=c_data.get("mentioned_count", 0),
                outcome=c_data.get("outcome", "")
            ))
        return system
