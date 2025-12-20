"""
Narrative Multiplayer System.

This module manages scenes with multiple protagonists, ensuring spotlight balance
and tracking individual character arcs within a shared scene.
"""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class NarrativeMultiplayerSystem:
    """
    Manages multiple active protagonists.
    """
    active_protagonists: List[str] = field(default_factory=list)
    spotlight_time: Dict[str, int] = field(default_factory=dict) # Count of mentions/focus
    
    def register_protagonist(self, name: str):
        if name not in self.active_protagonists:
            self.active_protagonists.append(name)
            self.spotlight_time[name] = 0

    def get_spotlight_guidance(self) -> str:
        """
        Suggest who needs narrative focus.
        """
        if not self.active_protagonists:
            return ""
            
        # Find who has the least spotlight
        # Sort by usage
        sorted_chars = sorted(self.active_protagonists, key=lambda p: self.spotlight_time.get(p, 0))
        least_focused = sorted_chars[0]
        
        return f"[SPOTLIGHT: Focus heavily on {least_focused}, they have been quiet recently.]"

    def record_mention(self, text: str):
        """
        Update spotlight counts based on output text.
        """
        for char in self.active_protagonists:
            if char in text:
                self.spotlight_time[char] = self.spotlight_time.get(char, 0) + 1

    def to_dict(self) -> dict:
        return {
            "active_protagonists": self.active_protagonists,
            "spotlight_time": self.spotlight_time
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeMultiplayerSystem":
        sys = cls()
        sys.active_protagonists = data.get("active_protagonists", [])
        sys.spotlight_time = data.get("spotlight_time", {})
        return sys
