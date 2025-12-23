"""Personality and emotional models for NPC reasoning."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PersonalityTraits:
    risk_taking: float = 0.5
    empathy: float = 0.5
    curiosity: float = 0.5
    patience: float = 0.5


@dataclass
class Drives:
    """High-level motivators that guide behavior selection."""

    survival: float = 0.6
    social: float = 0.5
    exploration: float = 0.5


@dataclass
class EmotionalState:
    """Lightweight emotional model driving biases."""

    current_state: str = "calm"
    intensity: float = 0.3

    def is_afraid(self) -> bool:
        return self.current_state.lower() in {"afraid", "anxious"} and self.intensity > 0.5

    def utility_bias(self) -> float:
        if self.current_state.lower() == "angry":
            return 1.1 + self.intensity * 0.2
        if self.is_afraid():
            return 0.7
        if self.current_state.lower() == "curious":
            return 1.0 + self.intensity * 0.1
        return 1.0


@dataclass
class PersonalityProfile:
    traits: PersonalityTraits = field(default_factory=PersonalityTraits)
    drives: Drives = field(default_factory=Drives)
    dialogue_tone: str = "neutral"

    def utility_modifier(self, goal) -> float:
        base = 1.0
        if "risk" in goal.name.lower():
            base += (self.traits.risk_taking - 0.5) * 0.6
        if "assist" in goal.name.lower():
            base += (self.traits.empathy - 0.5) * 0.5
        base += (self.traits.curiosity - 0.5) * 0.2
        return max(0.2, base)

    def modulate_dialogue(self, text: str) -> str:
        if self.dialogue_tone == "warm":
            return f"{text} (spoken gently)"
        if self.dialogue_tone == "cold":
            return f"{text} (terse)"
        return text
