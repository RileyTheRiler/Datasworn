"""
OCEAN Personality Model & Cinematography System.
Implements Big Five personality traits and shot selection.

OCEAN = Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
Cinematography = Wide/Medium/Close shot selection based on emotional context.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random


# ============================================================================
# OCEAN Personality Model (Big Five)
# ============================================================================

@dataclass
class OCEANProfile:
    """
    Big Five personality traits for an NPC.
    Each trait is 0.0 (low) to 1.0 (high).
    """
    openness: float = 0.5  # Creativity, curiosity vs. caution
    conscientiousness: float = 0.5  # Organization, dependability vs. careless
    extraversion: float = 0.5  # Outgoing, energetic vs. reserved
    agreeableness: float = 0.5  # Friendly, compassionate vs. antagonistic
    neuroticism: float = 0.5  # Sensitive, nervous vs. confident, calm
    
    def get_dialogue_style(self) -> dict:
        """Generate dialogue style guidance based on traits."""
        style = {
            "verbosity": "normal",
            "formality": "casual",
            "emotional_tone": "neutral",
            "confidence": "average",
            "friendliness": "neutral",
        }
        
        # Extraversion affects verbosity
        if self.extraversion > 0.7:
            style["verbosity"] = "talkative"
        elif self.extraversion < 0.3:
            style["verbosity"] = "terse"
        
        # Conscientiousness affects formality
        if self.conscientiousness > 0.7:
            style["formality"] = "formal"
        elif self.conscientiousness < 0.3:
            style["formality"] = "sloppy"
        
        # Neuroticism affects emotional tone
        if self.neuroticism > 0.7:
            style["emotional_tone"] = "anxious"
        elif self.neuroticism < 0.3:
            style["emotional_tone"] = "calm"
        
        # Agreeableness affects friendliness
        if self.agreeableness > 0.7:
            style["friendliness"] = "warm"
        elif self.agreeableness < 0.3:
            style["friendliness"] = "cold"
        
        # Openness affects confidence/creativity
        if self.openness > 0.7:
            style["confidence"] = "curious"
        elif self.openness < 0.3:
            style["confidence"] = "skeptical"
        
        return style
    
    def get_narrator_context(self, npc_name: str) -> str:
        """Generate narrator context for this personality."""
        style = self.get_dialogue_style()
        
        lines = [f"[PERSONALITY: {npc_name}]"]
        lines.append(f"OCEAN: O={self.openness:.1f} C={self.conscientiousness:.1f} "
                    f"E={self.extraversion:.1f} A={self.agreeableness:.1f} N={self.neuroticism:.1f}")
        
        # Generate personality description
        traits = []
        if self.openness > 0.6:
            traits.append("curious and imaginative")
        elif self.openness < 0.4:
            traits.append("practical and cautious")
        
        if self.conscientiousness > 0.6:
            traits.append("organized and reliable")
        elif self.conscientiousness < 0.4:
            traits.append("spontaneous and flexible")
        
        if self.extraversion > 0.6:
            traits.append("outgoing and energetic")
        elif self.extraversion < 0.4:
            traits.append("reserved and introspective")
        
        if self.agreeableness > 0.6:
            traits.append("kind and cooperative")
        elif self.agreeableness < 0.4:
            traits.append("competitive and skeptical")
        
        if self.neuroticism > 0.6:
            traits.append("sensitive and anxious")
        elif self.neuroticism < 0.4:
            traits.append("confident and stable")
        
        if traits:
            lines.append(f"Personality: {', '.join(traits)}")
        
        lines.append(f"Dialogue style: {style['verbosity']}, {style['formality']}, {style['friendliness']}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OCEANProfile":
        return cls(
            openness=data.get("openness", 0.5),
            conscientiousness=data.get("conscientiousness", 0.5),
            extraversion=data.get("extraversion", 0.5),
            agreeableness=data.get("agreeableness", 0.5),
            neuroticism=data.get("neuroticism", 0.5),
        )


# Pre-built personality archetypes
PERSONALITY_ARCHETYPES = {
    "hero": OCEANProfile(openness=0.7, conscientiousness=0.8, extraversion=0.6, agreeableness=0.7, neuroticism=0.3),
    "villain": OCEANProfile(openness=0.5, conscientiousness=0.7, extraversion=0.6, agreeableness=0.2, neuroticism=0.4),
    "mentor": OCEANProfile(openness=0.8, conscientiousness=0.7, extraversion=0.5, agreeableness=0.8, neuroticism=0.2),
    "trickster": OCEANProfile(openness=0.9, conscientiousness=0.3, extraversion=0.8, agreeableness=0.5, neuroticism=0.4),
    "guardian": OCEANProfile(openness=0.4, conscientiousness=0.9, extraversion=0.4, agreeableness=0.6, neuroticism=0.3),
    "rebel": OCEANProfile(openness=0.7, conscientiousness=0.3, extraversion=0.7, agreeableness=0.4, neuroticism=0.5),
    "sage": OCEANProfile(openness=0.9, conscientiousness=0.6, extraversion=0.3, agreeableness=0.7, neuroticism=0.2),
    "everyman": OCEANProfile(openness=0.5, conscientiousness=0.5, extraversion=0.5, agreeableness=0.6, neuroticism=0.5),
    "outlaw": OCEANProfile(openness=0.6, conscientiousness=0.2, extraversion=0.6, agreeableness=0.3, neuroticism=0.6),
    "caregiver": OCEANProfile(openness=0.5, conscientiousness=0.7, extraversion=0.6, agreeableness=0.9, neuroticism=0.4),
}


# ============================================================================
# Maslow's Hierarchy of Needs
# ============================================================================

class MaslowLevel(Enum):
    """Maslow's hierarchy levels."""
    PHYSIOLOGICAL = 1  # Food, water, shelter
    SAFETY = 2  # Security, stability
    LOVE_BELONGING = 3  # Friendship, family
    ESTEEM = 4  # Respect, recognition
    SELF_ACTUALIZATION = 5  # Purpose, meaning


@dataclass
class MaslowNeeds:
    """Tracks an NPC's needs hierarchy."""
    physiological: float = 1.0  # 0-1, 1 = fully satisfied
    safety: float = 1.0
    love_belonging: float = 0.5
    esteem: float = 0.5
    self_actualization: float = 0.3
    
    def get_dominant_need(self) -> MaslowLevel:
        """Get the most pressing unsatisfied need."""
        # Maslow's principle: lower needs must be met first
        if self.physiological < 0.3:
            return MaslowLevel.PHYSIOLOGICAL
        if self.safety < 0.3:
            return MaslowLevel.SAFETY
        if self.love_belonging < 0.3:
            return MaslowLevel.LOVE_BELONGING
        if self.esteem < 0.3:
            return MaslowLevel.ESTEEM
        return MaslowLevel.SELF_ACTUALIZATION
    
    def get_motivation_context(self) -> str:
        """Generate motivation context for narrator."""
        need = self.get_dominant_need()
        
        motivations = {
            MaslowLevel.PHYSIOLOGICAL: "Driven by hunger, thirst, or exhaustion. Will trade anything for basics.",
            MaslowLevel.SAFETY: "Desperate for security. Avoids risks, seeks protection.",
            MaslowLevel.LOVE_BELONGING: "Lonely. Seeks connection, acceptance, loyalty.",
            MaslowLevel.ESTEEM: "Craves recognition and respect. Prideful.",
            MaslowLevel.SELF_ACTUALIZATION: "Pursuing meaning and purpose. Idealistic.",
        }
        
        return f"[MOTIVATION: {need.name}]\n{motivations[need]}"
    
    def to_dict(self) -> dict:
        return {
            "physiological": self.physiological,
            "safety": self.safety,
            "love_belonging": self.love_belonging,
            "esteem": self.esteem,
            "self_actualization": self.self_actualization,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MaslowNeeds":
        return cls(**{k: data.get(k, 0.5) for k in ["physiological", "safety", "love_belonging", "esteem", "self_actualization"]})


# ============================================================================
# Cinematography System
# ============================================================================

class ShotType(Enum):
    """Types of cinematographic shots."""
    ESTABLISHING = "establishing"  # Wide - show environment
    WIDE = "wide"  # Full scene, multiple characters
    MEDIUM = "medium"  # Upper body, conversational
    CLOSE = "close"  # Face, emotional detail
    EXTREME_CLOSE = "extreme_close"  # Eyes, hands, specific detail
    OVER_SHOULDER = "over_shoulder"  # Dialogue framing
    POV = "pov"  # Player's direct view


@dataclass
class CinematographyDirector:
    """
    Selects appropriate "shot" framing for narrative descriptions.
    Based on emotional intensity and tactical complexity.
    """
    
    def select_shot(
        self,
        emotional_intensity: float,  # 0-1
        tactical_complexity: float,  # 0-1
        is_dialogue: bool = False,
        is_action: bool = False,
    ) -> ShotType:
        """Select the appropriate shot type."""
        # High emotion = zoom in
        if emotional_intensity > 0.8:
            return ShotType.EXTREME_CLOSE
        elif emotional_intensity > 0.6:
            return ShotType.CLOSE
        
        # High tactical = zoom out
        if tactical_complexity > 0.7:
            return ShotType.WIDE
        elif tactical_complexity > 0.5:
            return ShotType.ESTABLISHING
        
        # Dialogue defaults
        if is_dialogue:
            return ShotType.OVER_SHOULDER if emotional_intensity > 0.4 else ShotType.MEDIUM
        
        # Action defaults
        if is_action:
            return ShotType.MEDIUM
        
        return ShotType.MEDIUM
    
    def get_shot_guidance(self, shot: ShotType) -> str:
        """Generate narrator guidance for the selected shot."""
        guidance = {
            ShotType.ESTABLISHING: (
                "WIDE SHOT: Describe the environment first. Set the stage. "
                "Weather, lighting, scale. Characters are small in the frame."
            ),
            ShotType.WIDE: (
                "WIDE SHOT: Show the full scene. Multiple characters, their positions relative "
                "to each other. Tactical layout visible."
            ),
            ShotType.MEDIUM: (
                "MEDIUM SHOT: Focus on upper body. Gestures, posture, general demeanor. "
                "Some environment visible for context."
            ),
            ShotType.CLOSE: (
                "CLOSE-UP: Focus on the face. Micro-expressions matter. "
                "What do their eyes betray? The twitch of a lip?"
            ),
            ShotType.EXTREME_CLOSE: (
                "EXTREME CLOSE-UP: A single detail fills the frame. "
                "The white knuckles. The tear track. The trembling hand."
            ),
            ShotType.OVER_SHOULDER: (
                "OVER-SHOULDER: Frame the dialogue through one character's perspective. "
                "We see who they're talking to, their reaction."
            ),
            ShotType.POV: (
                "POV SHOT: We see exactly what the player sees. First-person immediacy. "
                "Describe through their senses directly."
            ),
        }
        return guidance.get(shot, guidance[ShotType.MEDIUM])
    
    def get_narrator_context(
        self,
        emotional_intensity: float,
        tactical_complexity: float,
        is_dialogue: bool = False,
        is_action: bool = False,
    ) -> str:
        """Generate full cinematography context for narrator."""
        shot = self.select_shot(emotional_intensity, tactical_complexity, is_dialogue, is_action)
        guidance = self.get_shot_guidance(shot)
        
        return f"[CINEMATOGRAPHY: {shot.value.upper()}]\n{guidance}"


# ============================================================================
# Convenience Functions
# ============================================================================

def create_personality(archetype: str = "everyman") -> OCEANProfile:
    """Create a personality from archetype."""
    return PERSONALITY_ARCHETYPES.get(archetype, PERSONALITY_ARCHETYPES["everyman"])


def create_random_personality() -> OCEANProfile:
    """Create a randomized personality."""
    return OCEANProfile(
        openness=random.uniform(0.2, 0.8),
        conscientiousness=random.uniform(0.2, 0.8),
        extraversion=random.uniform(0.2, 0.8),
        agreeableness=random.uniform(0.2, 0.8),
        neuroticism=random.uniform(0.2, 0.8),
    )


def get_cinematography_context(
    emotional_intensity: float,
    tactical_complexity: float = 0.0,
) -> str:
    """Quick cinematography context generation."""
    director = CinematographyDirector()
    return director.get_narrator_context(
        emotional_intensity=emotional_intensity,
        tactical_complexity=tactical_complexity,
    )
