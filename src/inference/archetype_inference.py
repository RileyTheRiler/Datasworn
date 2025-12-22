"""
Archetype Inference Engine - Updates archetype profile based on observations.

This module takes behavior observations and updates the player's archetype
profile, applying decay to old signals and detecting significant shifts.
"""

from datetime import datetime
from typing import List, Optional, Dict
from src.narrative.archetype_types import (
    ArchetypeProfile,
    BehaviorInstance,
    NeedState,
    ArchetypeShift,
)
from src.config.archetype_config_loader import get_config_loader, InferenceConfig


class ArchetypeInferenceEngine:
    """
    Updates archetype profile based on behavior observations.
    
    The engine:
    1. Applies decay to existing weights (old patterns fade)
    2. Adds new signals with appropriate weights
    3. Normalizes to maintain distribution
    4. Updates meta-layer (overcontrolled/undercontrolled tendencies)
    5. Recalculates confidence
    6. Detects significant shifts
    """
    
    def __init__(self, config: Optional[InferenceConfig] = None):
        self.config_loader = get_config_loader()
        if config is None:
            config = self.config_loader.get_inference_config()
        self.config = config
    
    def update_profile(
        self,
        current_profile: ArchetypeProfile,
        new_observations: List[BehaviorInstance],
    ) -> ArchetypeProfile:
        """
        Updates the weighted profile based on new observations.
        
        Args:
            current_profile: The current archetype profile
            new_observations: List of new behavior observations
            
        Returns:
            Updated archetype profile
        """
        # Step 1: Apply decay to existing weights
        decayed_profile = self._apply_decay(current_profile)
        
        # Step 2: Add new signals
        updated_profile = self._add_signals(decayed_profile, new_observations)
        
        # Step 3: Normalize weights
        normalized_profile = self._normalize_weights(updated_profile)
        
        # Step 4: Update meta-layer
        final_profile = self._update_meta_layer(normalized_profile)
        
        # Step 5: Update tracking fields
        final_profile.observation_count += len(new_observations)
        final_profile.last_updated = datetime.now()
        
        return final_profile
    
    def infer_needs(
        self,
        profile: ArchetypeProfile,
        observations: List[BehaviorInstance],
    ) -> NeedState:
        """
        Infers psychological and moral needs from the profile.
        
        Uses the archetype definitions to determine:
        - What wound does this archetype indicate?
        - What need does that wound create?
        - What moral corruption flows from that wound?
        - What moral need does that create?
        
        Args:
            profile: Current archetype profile
            observations: Recent behavior observations for evidence
            
        Returns:
            NeedState with inferred needs and evidence
        """
        primary = profile.primary_archetype
        
        if primary == "unknown":
            return NeedState()
        
        # Get archetype definition
        archetype_def = self.config_loader.get_archetype(primary)
        
        # Extract needs from definition
        need_state = NeedState(
            psychological_wound=archetype_def.psychological_wound,
            psychological_need=archetype_def.psychological_need,
            moral_corruption=archetype_def.moral_corruption,
            moral_need=archetype_def.moral_need,
        )
        
        # Calculate awareness based on observation count and confidence
        # More observations + higher confidence = higher awareness
        awareness = min(1.0, (profile.observation_count / 20.0) * profile.confidence)
        need_state.psychological_awareness = awareness
        need_state.moral_awareness = awareness * 0.8  # Moral awareness lags slightly
        
        # Collect evidence from observations
        for obs in observations:
            if primary in obs.archetype_signals:
                # This observation supports the primary archetype
                if obs.npc_involved:
                    # If it involves an NPC, it might be moral evidence
                    need_state.moral_evidence.append(obs)
                else:
                    # Otherwise, psychological evidence
                    need_state.psychological_evidence.append(obs)
        
        # Create wound-to-corruption chain
        need_state.wound_to_corruption_chain = (
            f"The {archetype_def.psychological_wound} leads to "
            f"{archetype_def.moral_corruption}, which requires "
            f"{archetype_def.moral_need} to overcome."
        )
        
        return need_state
    
    def detect_shift(
        self,
        old_profile: ArchetypeProfile,
        new_profile: ArchetypeProfile,
        trigger_behavior: Optional[BehaviorInstance] = None,
    ) -> Optional[ArchetypeShift]:
        """
        Detects if a significant shift has occurred.
        
        Returns shift info if:
        - Primary archetype changed
        - Secondary archetype became primary
        - Significant weight redistribution
        
        Args:
            old_profile: Previous archetype profile
            new_profile: Updated archetype profile
            trigger_behavior: The behavior that may have triggered the shift
            
        Returns:
            ArchetypeShift if significant shift detected, None otherwise
        """
        old_primary = old_profile.primary_archetype
        new_primary = new_profile.primary_archetype
        
        # Check if primary archetype changed
        if old_primary != new_primary:
            # Calculate shift magnitude
            old_weight = old_profile.get_weight(old_primary)
            new_weight = new_profile.get_weight(new_primary)
            magnitude = abs(new_weight - old_weight)
            
            # Only count as shift if magnitude exceeds threshold
            if magnitude >= self.config.shift_threshold:
                return ArchetypeShift(
                    timestamp=datetime.now(),
                    old_primary=old_primary,
                    new_primary=new_primary,
                    trigger_behavior=trigger_behavior,
                    shift_magnitude=magnitude,
                )
        
        return None
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _apply_decay(self, profile: ArchetypeProfile) -> ArchetypeProfile:
        """Apply decay to all archetype weights."""
        decayed = ArchetypeProfile()
        
        for archetype in self.config_loader.get_archetype_names():
            current_weight = profile.get_weight(archetype)
            decayed_weight = current_weight * self.config.decay_rate
            decayed.set_weight(archetype, decayed_weight)
        
        # Copy tracking fields
        decayed.observation_count = profile.observation_count
        decayed.last_updated = profile.last_updated
        
        return decayed
    
    def _add_signals(
        self,
        profile: ArchetypeProfile,
        observations: List[BehaviorInstance],
    ) -> ArchetypeProfile:
        """Add new signals from observations to the profile."""
        updated = ArchetypeProfile()
        
        # Start with current weights
        for archetype in self.config_loader.get_archetype_names():
            updated.set_weight(archetype, profile.get_weight(archetype))
        
        # Add signals from each observation
        for obs in observations:
            for archetype, signal_strength in obs.archetype_signals.items():
                current_weight = updated.get_weight(archetype)
                # Add signal strength, scaled down to prevent runaway growth
                new_weight = current_weight + (signal_strength * 0.1)
                updated.set_weight(archetype, new_weight)
        
        # Copy tracking fields
        updated.observation_count = profile.observation_count
        updated.last_updated = profile.last_updated
        
        return updated
    
    def _normalize_weights(self, profile: ArchetypeProfile) -> ArchetypeProfile:
        """Normalize weights to maintain reasonable distribution."""
        normalized = ArchetypeProfile()
        
        # Calculate total weight
        total_weight = sum(
            profile.get_weight(archetype)
            for archetype in self.config_loader.get_archetype_names()
        )
        
        if total_weight == 0:
            # No signals yet, return as-is
            return profile
        
        # Normalize each weight
        for archetype in self.config_loader.get_archetype_names():
            current_weight = profile.get_weight(archetype)
            normalized_weight = current_weight / total_weight
            normalized.set_weight(archetype, normalized_weight)
        
        # Copy tracking fields
        normalized.observation_count = profile.observation_count
        normalized.last_updated = profile.last_updated
        
        return normalized
    
    def _update_meta_layer(self, profile: ArchetypeProfile) -> ArchetypeProfile:
        """Update overcontrolled/undercontrolled tendency aggregates."""
        overcontrolled_archetypes = self.config_loader.get_archetypes_by_cluster("overcontrolled")
        undercontrolled_archetypes = self.config_loader.get_archetypes_by_cluster("undercontrolled")
        
        # Calculate aggregate tendencies
        overcontrolled_total = sum(
            profile.get_weight(archetype)
            for archetype in overcontrolled_archetypes
        )
        
        undercontrolled_total = sum(
            profile.get_weight(archetype)
            for archetype in undercontrolled_archetypes
        )
        
        profile.overcontrolled_tendency = overcontrolled_total
        profile.undercontrolled_tendency = undercontrolled_total
        
        return profile
