"""
Character Identity System for Starforged AI Game Master.
Tracks the emerging persona of the player character based on their narrative choices.
Detects dissonance when actions conflict with established character identity.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from datetime import datetime
from src.narrative.revelation_tracking import RevelationStage

class IdentityArchetype(str, Enum):
    BRUTE = "brute"          # High violence, direct action, iron-willed.
    SHADOW = "shadow"        # Stealth, deception, indirect approach.
    DIPLOMAT = "diplomat"    # Empathy, negotiation, social grace.
    SCHOLAR = "scholar"      # Logic, research, curiosity.
    RAIDER = "raider"        # Greed, ambition, opportunism.
    GUARDIAN = "guardian"    # Protection, altruism, justice.
    UNKNOWN = "unknown"      # Baseline/Initial state.

class RUOType(str, Enum):
    RESILIENT = "resilient"              # Balanced, flexible, adaptive
    OVERCONTROLLED = "overcontrolled"      # Rigid, anxious, inhibited
    UNDERCONTROLLED = "undercontrolled"    # Impulsive, volatile, uninhibited
    UNKNOWN = "unknown"

class WoundType(str, Enum):
    # Overcontrolled Cluster
    CONTROLLER = "controller"         # Fear of chaos/helplessness
    JUDGE = "judge"                   # Fear of moral ambiguity
    GHOST = "ghost"                   # Fear of attachment/loss
    PERFECTIONIST = "perfectionist"   # Fear of inadequacy/failure
    MARTYR = "martyr"                 # Fear of worthlessness unless suffering
    ASCETIC = "ascetic"               # Fear of desire/pleasure
    PARANOID = "paranoid"             # Fear of vulnerability/betrayal
    PEDANT = "pedant"                 # Fear of being wrong

    # Undercontrolled Cluster
    CYNIC = "cynic"                   # Shattered faith in humanity
    FUGITIVE = "fugitive"             # Shame over past actions
    HEDONIST = "hedonist"             # Fear of missing out/emptiness
    DESTROYER = "destroyer"           # Rage at injustice/powerlessness
    TRICKSTER = "trickster"           # Fear of being trapped/controlled
    NARCISSIST = "narcissist"         # Buried shame/inadequacy
    PREDATOR = "predator"             # Disconnection from consequence
    MANIPULATOR = "manipulator"       # Fear of powerlessness

    # Hybrid/Complex
    IMPOSTOR = "impostor"             # Fear of being exposed as fraud
    SAVIOR = "savior"                 # Fear of being unneeded
    AVENGER = "avenger"               # Grief transformed to rage
    COWARD = "coward"                 # Overwhelming fear
    ZEALOT = "zealot"                 # Fear of meaninglessness
    FLATTERER = "flatterer"           # Fear of rejection
    MISER = "miser"                   # Fear of scarcity/loss
    
    UNKNOWN = "unknown"

@dataclass
class IdentityScore:
    violence: float = 0.0    # Tendency toward force/combat.
    stealth: float = 0.0     # Tendency toward deception/sneakiness.
    empathy: float = 0.0     # Tendency toward helping/negotiating.
    logic: float = 0.0       # Tendency toward cold calculation/reason.
    greed: float = 0.0       # Tendency toward personal gain.
    
    def to_dict(self) -> dict:
        return {
            "violence": self.violence,
            "stealth": self.stealth,
            "empathy": self.empathy,
            "logic": self.logic,
            "greed": self.greed
        }

@dataclass
class WoundScore:
    """Tracks scores for all 22 archetypes. Using a dictionary for flexibility."""
    scores: Dict[WoundType, float] = field(default_factory=dict)
    
    def __post_init__(self):
        # Initialize all wounds to 0.0 if empty
        if not self.scores:
            for wound in WoundType:
                if wound != WoundType.UNKNOWN:
                    self.scores[wound] = 0.0
    
    def to_dict(self) -> dict:
        return {k.value: v for k, v in self.scores.items()}

@dataclass
class WoundProfile:
    dominant_wound: WoundType = WoundType.UNKNOWN
    secondary_wound: WoundType = WoundType.UNKNOWN
    tertiary_wound: WoundType = WoundType.UNKNOWN
    
    scores: WoundScore = field(default_factory=WoundScore)
    
    ruo_tendency: Dict[RUOType, float] = field(default_factory=lambda: {
        RUOType.RESILIENT: 0.0,
        RUOType.OVERCONTROLLED: 0.0,
        RUOType.UNDERCONTROLLED: 0.0
    })
    
    philosophical_need: str = ""
    moral_need: str = ""
    dark_wisdom: str = ""
    
    revelation_progress: float = 0.0  # 0.0 to 1.0
    is_revealed: bool = False
    revelation_history: List[RevelationStage] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "dominant_wound": self.dominant_wound.value,
            "secondary_wound": self.secondary_wound.value,
            "tertiary_wound": self.tertiary_wound.value,
            "scores": self.scores.to_dict(),
            "ruo_tendency": {k.value: v for k, v in self.ruo_tendency.items()},
            "philosophical_need": self.philosophical_need,
            "moral_need": self.moral_need,
            "dark_wisdom": self.dark_wisdom,
            "revelation_progress": self.revelation_progress,
            "is_revealed": self.is_revealed,
            "revelation_history": [r.to_dict() for r in self.revelation_history]
        }

@dataclass
class ChoiceRecord:
    description: str
    impact: IdentityScore
    timestamp: datetime = field(default_factory=datetime.now)

class CharacterIdentity(BaseModel):
    archetype: IdentityArchetype = IdentityArchetype.UNKNOWN
    scores: IdentityScore = Field(default_factory=IdentityScore)
    choice_history: List[ChoiceRecord] = Field(default_factory=list)
    dissonance_score: float = 0.0  # 0.0 (consistent) to 1.0 (highly dissonant)
    wound_profile: WoundProfile = Field(default_factory=WoundProfile)
    
    class Config:
        arbitrary_types_allowed = True

    def update_scores(self, impact: IdentityScore, description: str):
        """Update scores and track choice history."""
        # Calculate dissonance before updating
        dissonance = self._calculate_dissonance(impact)
        
        # Dampen dissonance growth but make it persistent
        self.dissonance_score = min(1.0, self.dissonance_score * 0.9 + dissonance * 0.2)
        
        # Update scores
        self.scores.violence = max(0.0, min(1.0, self.scores.violence + impact.violence))
        self.scores.stealth = max(0.0, min(1.0, self.scores.stealth + impact.stealth))
        self.scores.empathy = max(0.0, min(1.0, self.scores.empathy + impact.empathy))
        self.scores.logic = max(0.0, min(1.0, self.scores.logic + impact.logic))
        self.scores.greed = max(0.0, min(1.0, self.scores.greed + impact.greed))
        
        self.choice_history.append(ChoiceRecord(description=description, impact=impact))
        self._set_archetype()

    def _calculate_dissonance(self, impact: IdentityScore) -> float:
        """Calculate how much an action conflicts with the current persona."""
        if self.archetype == IdentityArchetype.UNKNOWN:
            return 0.0
            
        dissonance = 0.0
        
        # Example conflicts:
        # A Brute (low stealth preference, high violence) being stealthy/submissive.
        if self.archetype == IdentityArchetype.BRUTE:
            if impact.stealth > 0.05: dissonance += impact.stealth
            if impact.empathy > 0.05: dissonance += impact.empathy * 0.5
            
        elif self.archetype == IdentityArchetype.SHADOW:
            if impact.violence > 0.1: dissonance += impact.violence
            if impact.logic > 0.1: dissonance += impact.logic * 0.3
            
        elif self.archetype == IdentityArchetype.DIPLOMAT:
            if impact.violence > 0.1: dissonance += impact.violence
            if impact.greed > 0.1: dissonance += impact.greed * 0.4
            
        elif self.archetype == IdentityArchetype.SCHOLAR:
            if impact.violence > 0.6: dissonance += impact.violence * 0.5
            
        return min(1.0, dissonance)

    def _set_archetype(self):
        """Determine archetype based on dominant score."""
        s = self.scores
        max_score = max(s.violence, s.stealth, s.empathy, s.logic, s.greed)
        
        if max_score < 0.1:
            self.archetype = IdentityArchetype.UNKNOWN
            return
            
        if s.violence == max_score: self.archetype = IdentityArchetype.BRUTE
        elif s.stealth == max_score: self.archetype = IdentityArchetype.SHADOW
        elif s.empathy == max_score: self.archetype = IdentityArchetype.DIPLOMAT
        elif s.logic == max_score: self.archetype = IdentityArchetype.SCHOLAR
        elif s.greed == max_score: self.archetype = IdentityArchetype.RAIDER

    def to_dict(self) -> dict:
        return {
            "archetype": self.archetype.value,
            "scores": self.scores.to_dict(),
            "dissonance_score": self.dissonance_score,
            "wound_profile": self.wound_profile.to_dict(),
            "recent_choices": [c.description for c in self.choice_history[-5:]]
        }
