"""
Flashback System.

This module manages "Memory Scenes" where the player relives a past moment,
handling the state transition between Present and Past.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class FlashbackSystem:
    """
    Manages flashback state.
    """
    is_active: bool = False
    original_scene_id: int = 0
    flashback_depth: int = 0
    
    def start_flashback(self, current_scene_id: int):
        """Enter memory mode."""
        self.is_active = True
        self.original_scene_id = current_scene_id
        self.flashback_depth += 1

    def end_flashback(self) -> int:
        """Return to present."""
        self.is_active = False
        self.flashback_depth = 0
        return self.original_scene_id

    def get_context_prefix(self) -> str:
        """
        Get text to prepend to narrator prompts.
        """
        if self.is_active:
            return "[MODE: FLASHBACK - DESCRIBE EVENTS IN THE PAST TENSE. THIS IS A MEMORY.]"
        return ""

    def to_dict(self) -> dict:
        return {
            "is_active": self.is_active,
            "original_scene_id": self.original_scene_id,
            "flashback_depth": self.flashback_depth
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FlashbackSystem":
        sys = cls()
        sys.is_active = data.get("is_active", False)
        sys.original_scene_id = data.get("original_scene_id", 0)
        sys.flashback_depth = data.get("flashback_depth", 0)
        return sys
