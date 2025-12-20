"""
Unreliable Narrator System.

This module introduces bias, distortion, and potential hallucinations into the
narrative based on the character's mental state.
"""

from dataclasses import dataclass
import random

@dataclass
class UnreliableNarratorSystem:
    """
    Manages narrative distortion.
    """
    sanity_level: float = 1.0 # 1.0 = Sane, 0.0 = Insane
    stress_level: float = 0.0 # 0.0 = Calm, 1.0 = Panic
    
    def get_distortion_level(self) -> str:
        if self.sanity_level < 0.3:
            return "SEVERE_DISTORTION"
        elif self.sanity_level < 0.6:
            return "MILD_DISTORTION"
        elif self.stress_level > 0.8:
            return "PANIC_BIAS"
        return "NONE"

    def get_narrator_instruction(self) -> str:
        """
        Get instructions for the LLM to warp the text.
        """
        level = self.get_distortion_level()
        
        if level == "SEVERE_DISTORTION":
            return (
                "[WARNING: UNRELIABLE NARRATOR ACTIVE]\n"
                "The protagonist is losing their grip on reality. "
                "Describe things that might not be there. "
                "Twist innocent details into threats. "
                "The shadows are watching."
            )
        elif level == "MILD_DISTORTION":
            return (
                "[NOTE: SUBJECTIVE NARRATION]\n"
                "The protagonist is paranoid. "
                "Mention subtle wrongness in the environment. "
                "Voices sound distant or mocking."
            )
        elif level == "PANIC_BIAS":
            return (
                "[NOTE: HIGH STRESS]\n"
                "Description should be fragmented, rushed, and focused on immediate danger. "
                "Tunnel vision effect."
            )
            
        return ""

    def to_dict(self) -> dict:
        return {
            "sanity_level": self.sanity_level,
            "stress_level": self.stress_level
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UnreliableNarratorSystem":
        sys = cls()
        sys.sanity_level = data.get("sanity_level", 1.0)
        sys.stress_level = data.get("stress_level", 0.0)
        return sys
