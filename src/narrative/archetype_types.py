"""
Core data structures for the narrative psychology archetype system.

This module defines the 22 archetypes across 3 clusters (Overcontrolled,
Undercontrolled, Hybrid) and tracks player behavior patterns, psychological
needs, and revelation progress.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum


# ============================================================================
# Archetype Clusters
# ============================================================================

class ArchetypeCluster(str, Enum):
    """Three main clusters of archetypes."""
    OVERCONTROLLED = "overcontrolled"
    UNDERCONTROLLED = "undercontrolled"
    HYBRID = "hybrid"


# ============================================================================
# Archetype Profile
# ============================================================================

@dataclass
class ArchetypeProfile:
    """
    Weighted profile across all 22 archetypes.
    
    Each archetype has a weight (0.0-1.0) representing how strongly
    the player exhibits that pattern. Weights are updated based on
    observed behaviors.
    """
    
    # Overcontrolled Cluster (8 archetypes)
    controller: float = 0.0
    judge: float = 0.0
    ghost: float = 0.0
    perfectionist: float = 0.0
    martyr: float = 0.0
    ascetic: float = 0.0
    paranoid: float = 0.0
    pedant: float = 0.0
    
    # Undercontrolled Cluster (8 archetypes)
    cynic: float = 0.0
    fugitive: float = 0.0
    hedonist: float = 0.0
    destroyer: float = 0.0
    trickster: float = 0.0
    narcissist: float = 0.0
    predator: float = 0.0
    manipulator: float = 0.0
    
    # Hybrid Cluster (6 archetypes)
    impostor: float = 0.0
    savior: float = 0.0
    avenger: float = 0.0
    coward: float = 0.0
    zealot: float = 0.0
    flatterer: float = 0.0
    
    # Meta-layer aggregates
    overcontrolled_tendency: float = 0.0
    undercontrolled_tendency: float = 0.0
    
    # Tracking
    observation_count: int = 0
    last_updated: Optional[datetime] = None
    
    @property
    def primary_archetype(self) -> str:
        """Returns the highest-weighted archetype."""
        weights = self._get_archetype_weights()
        if not weights:
            return "unknown"
        return max(weights.items(), key=lambda x: x[1])[0]
    
    @property
    def secondary_archetype(self) -> str:
        """Returns the second-highest weighted archetype."""
        weights = self._get_archetype_weights()
        if len(weights) < 2:
            return "unknown"
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        return sorted_weights[1][0]
    
    @property
    def tertiary_archetype(self) -> str:
        """Returns the third-highest weighted archetype."""
        weights = self._get_archetype_weights()
        if len(weights) < 3:
            return "unknown"
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        return sorted_weights[2][0]
    
    @property
    def confidence(self) -> float:
        """
        How confident are we in the profile? (0-1)
        
        Based on:
        - Separation between primary and secondary archetypes
        - Number of observations
        """
        weights = self._get_archetype_weights()
        if len(weights) < 2 or self.observation_count < 5:
            return 0.0
        
        sorted_weights = sorted(weights.values(), reverse=True)
        primary_weight = sorted_weights[0]
        secondary_weight = sorted_weights[1]
        
        # Separation component (0-1)
        separation = min(1.0, (primary_weight - secondary_weight) * 2)
        
        # Observation component (0-1, asymptotic to 1)
        observation_factor = min(1.0, self.observation_count / 20.0)
        
        # Combined confidence
        return (separation * 0.6) + (observation_factor * 0.4)
    
    def _get_archetype_weights(self) -> Dict[str, float]:
        """Returns all archetype weights as a dictionary."""
        return {
            # Overcontrolled
            "controller": self.controller,
            "judge": self.judge,
            "ghost": self.ghost,
            "perfectionist": self.perfectionist,
            "martyr": self.martyr,
            "ascetic": self.ascetic,
            "paranoid": self.paranoid,
            "pedant": self.pedant,
            # Undercontrolled
            "cynic": self.cynic,
            "fugitive": self.fugitive,
            "hedonist": self.hedonist,
            "destroyer": self.destroyer,
            "trickster": self.trickster,
            "narcissist": self.narcissist,
            "predator": self.predator,
            "manipulator": self.manipulator,
            # Hybrid
            "impostor": self.impostor,
            "savior": self.savior,
            "avenger": self.avenger,
            "coward": self.coward,
            "zealot": self.zealot,
            "flatterer": self.flatterer,
        }
    
    def get_weight(self, archetype: str) -> float:
        """Get the weight for a specific archetype."""
        return self._get_archetype_weights().get(archetype, 0.0)
    
    def set_weight(self, archetype: str, weight: float):
        """Set the weight for a specific archetype."""
        weight = max(0.0, min(1.0, weight))  # Clamp to [0, 1]
        setattr(self, archetype, weight)
    
    def get_cluster(self, archetype: str) -> ArchetypeCluster:
        """Get the cluster for a specific archetype."""
        overcontrolled = ["controller", "judge", "ghost", "perfectionist", 
                         "martyr", "ascetic", "paranoid", "pedant"]
        undercontrolled = ["cynic", "fugitive", "hedonist", "destroyer",
                          "trickster", "narcissist", "predator", "manipulator"]
        
        if archetype in overcontrolled:
            return ArchetypeCluster.OVERCONTROLLED
        elif archetype in undercontrolled:
            return ArchetypeCluster.UNDERCONTROLLED
        else:
            return ArchetypeCluster.HYBRID
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "archetypes": self._get_archetype_weights(),
            "primary": self.primary_archetype,
            "secondary": self.secondary_archetype,
            "tertiary": self.tertiary_archetype,
            "confidence": self.confidence,
            "overcontrolled_tendency": self.overcontrolled_tendency,
            "undercontrolled_tendency": self.undercontrolled_tendency,
            "observation_count": self.observation_count,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


# ============================================================================
# Behavior Instance
# ============================================================================

@dataclass
class BehaviorInstance:
    """
    A single observed behavior that provides archetype signals.
    """
    scene_id: str
    timestamp: datetime
    behavior_type: str  # "dialogue", "action", "interrogation", "crisis"
    behavior_description: str
    archetype_signals: Dict[str, float]  # archetype -> signal strength
    context: str
    npc_involved: Optional[str] = None
    
    # For evidence chains
    related_need: Optional[str] = None  # "psychological" or "moral"
    harm_caused: Optional[str] = None  # If moral, who was hurt and how
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "scene_id": self.scene_id,
            "timestamp": self.timestamp.isoformat(),
            "behavior_type": self.behavior_type,
            "behavior_description": self.behavior_description,
            "archetype_signals": self.archetype_signals,
            "context": self.context,
            "npc_involved": self.npc_involved,
            "related_need": self.related_need,
            "harm_caused": self.harm_caused,
        }


# ============================================================================
# Need State
# ============================================================================

@dataclass
class NeedState:
    """
    Tracks psychological and moral needs.
    
    Psychological Need: What hurts the player themselves
    Moral Need: What causes the player to hurt others
    """
    
    # Psychological Need (hurts self)
    psychological_wound: str = "unknown"  # e.g., "fear_of_chaos"
    psychological_need: str = "unknown"   # e.g., "accept_uncertainty"
    psychological_awareness: float = 0.0  # 0-1, how aware is player?
    
    # Moral Need (hurts others)
    moral_corruption: str = "unknown"     # e.g., "treats_people_as_means"
    moral_need: str = "unknown"           # e.g., "respect_autonomy"
    moral_awareness: float = 0.0          # 0-1, how aware is player?
    
    # Evidence
    psychological_evidence: List[BehaviorInstance] = field(default_factory=list)
    moral_evidence: List[BehaviorInstance] = field(default_factory=list)
    
    # Connection (Truby: moral grows from psychological)
    wound_to_corruption_chain: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "psychological_wound": self.psychological_wound,
            "psychological_need": self.psychological_need,
            "psychological_awareness": self.psychological_awareness,
            "moral_corruption": self.moral_corruption,
            "moral_need": self.moral_need,
            "moral_awareness": self.moral_awareness,
            "psychological_evidence_count": len(self.psychological_evidence),
            "moral_evidence_count": len(self.moral_evidence),
            "wound_to_corruption_chain": self.wound_to_corruption_chain,
        }


# ============================================================================
# Revelation Progress
# ============================================================================

@dataclass
class SceneRecord:
    """Record of a revelation scene."""
    scene_id: str
    timestamp: datetime
    revelation_type: str
    content: str
    player_response: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "scene_id": self.scene_id,
            "timestamp": self.timestamp.isoformat(),
            "revelation_type": self.revelation_type,
            "content": self.content,
            "player_response": self.player_response,
        }


@dataclass
class RevelationProgress:
    """
    Tracks progress through the revelation ladder.
    
    The player progresses through micro-revelations that build
    toward the final confrontation with Yuki.
    """
    
    # Micro-revelations (progressive awareness)
    mirror_moment_delivered: bool = False      # 25% - saw pattern externally
    cost_revealed: bool = False                 # 40% - pattern hurt someone
    origin_glimpsed: bool = False               # 55% - backstory connection
    choice_crystallized: bool = False           # 70% - Ember named it
    
    # Final revelation
    murder_solution_delivered: bool = False     # 85% - confronted Yuki
    mirror_speech_given: bool = False           # Yuki connected it to player
    
    # Post-revelation
    moral_decision_made: bool = False
    moral_decision_choice: Optional[str] = None  # What they chose
    path_determined: Optional[str] = None        # "hero" or "tragedy"
    
    # Tracking
    revelation_scenes: List[SceneRecord] = field(default_factory=list)
    
    @property
    def current_stage(self) -> str:
        """Returns the current revelation stage."""
        if self.path_determined:
            return "complete"
        elif self.moral_decision_made:
            return "post_revelation"
        elif self.mirror_speech_given:
            return "final_revelation"
        elif self.murder_solution_delivered:
            return "confrontation"
        elif self.choice_crystallized:
            return "choice_crystallized"
        elif self.origin_glimpsed:
            return "origin_glimpsed"
        elif self.cost_revealed:
            return "cost_revealed"
        elif self.mirror_moment_delivered:
            return "mirror_moment"
        else:
            return "building"
    
    @property
    def progress_percentage(self) -> float:
        """Returns progress as a percentage (0-100)."""
        stages = [
            self.mirror_moment_delivered,
            self.cost_revealed,
            self.origin_glimpsed,
            self.choice_crystallized,
            self.murder_solution_delivered,
            self.mirror_speech_given,
            self.moral_decision_made,
        ]
        completed = sum(1 for stage in stages if stage)
        return (completed / len(stages)) * 100
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "mirror_moment_delivered": self.mirror_moment_delivered,
            "cost_revealed": self.cost_revealed,
            "origin_glimpsed": self.origin_glimpsed,
            "choice_crystallized": self.choice_crystallized,
            "murder_solution_delivered": self.murder_solution_delivered,
            "mirror_speech_given": self.mirror_speech_given,
            "moral_decision_made": self.moral_decision_made,
            "moral_decision_choice": self.moral_decision_choice,
            "path_determined": self.path_determined,
            "current_stage": self.current_stage,
            "progress_percentage": self.progress_percentage,
            "revelation_scenes_count": len(self.revelation_scenes),
        }


# ============================================================================
# Archetype Shift
# ============================================================================

@dataclass
class ArchetypeShift:
    """
    Records a significant shift in archetype profile.
    """
    timestamp: datetime
    old_primary: str
    new_primary: str
    trigger_behavior: Optional[BehaviorInstance] = None
    shift_magnitude: float = 0.0  # How significant was the shift
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "old_primary": self.old_primary,
            "new_primary": self.new_primary,
            "shift_magnitude": self.shift_magnitude,
            "trigger_behavior": self.trigger_behavior.to_dict() if self.trigger_behavior else None,
        }
