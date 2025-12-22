"""
Camp Arc State Machines.

Tracks character relationship levels, morale, arc progression,
and flags for mission integration.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ArcStep(Enum):
    """Stages of a character's narrative arc."""
    INTRODUCTION = "introduction"
    TRUST_BUILDING = "trust_building"
    CONFLICT = "conflict"
    RESOLUTION = "resolution"
    EPILOGUE = "epilogue"


@dataclass
class ArcState:
    """State of an NPC's narrative arc."""
    npc_id: str
    relationship_level: float = 0.5  # 0-1, synced with RelationshipWeb
    morale: float = 0.5  # 0-1, individual morale
    current_step: ArcStep = ArcStep.INTRODUCTION
    flags: set[str] = field(default_factory=set)
    interactions_count: int = 0
    key_moments: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "npc_id": self.npc_id,
            "relationship_level": self.relationship_level,
            "morale": self.morale,
            "current_step": self.current_step.value,
            "flags": list(self.flags),
            "interactions_count": self.interactions_count,
            "key_moments": self.key_moments[-5:],  # Last 5
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ArcState":
        return cls(
            npc_id=data.get("npc_id", ""),
            relationship_level=data.get("relationship_level", 0.5),
            morale=data.get("morale", 0.5),
            current_step=ArcStep(data.get("current_step", "introduction")),
            flags=set(data.get("flags", [])),
            interactions_count=data.get("interactions_count", 0),
            key_moments=data.get("key_moments", []),
        )


class CampArcManager:
    """Manages character arc progression and state."""
    
    def __init__(self):
        self.arc_states: dict[str, ArcState] = {}
        self.crew_morale: float = 0.5  # Overall crew morale
        
        # Initialize all crew members
        self._initialize_arcs()
    
    def _initialize_arcs(self) -> None:
        """Initialize arc states for all crew members."""
        crew = ["yuki", "torres", "kai", "okonkwo", "vasquez", "ember"]
        for npc_id in crew:
            self.arc_states[npc_id] = ArcState(npc_id=npc_id)
    
    def get_arc_state(self, npc_id: str) -> Optional[ArcState]:
        """Get the arc state for an NPC."""
        return self.arc_states.get(npc_id)
    
    def advance_arc(self, npc_id: str, force_step: Optional[ArcStep] = None) -> bool:
        """
        Advance an NPC's arc to the next step.
        Returns True if arc advanced.
        """
        state = self.arc_states.get(npc_id)
        if not state:
            return False
        
        if force_step:
            state.current_step = force_step
            return True
        
        # Auto-advance based on relationship and interactions
        step_order = [
            ArcStep.INTRODUCTION,
            ArcStep.TRUST_BUILDING,
            ArcStep.CONFLICT,
            ArcStep.RESOLUTION,
            ArcStep.EPILOGUE
        ]
        
        try:
            current_idx = step_order.index(state.current_step)
            
            # Check if ready to advance
            ready = False
            if state.current_step == ArcStep.INTRODUCTION and state.interactions_count >= 3:
                ready = True
            elif state.current_step == ArcStep.TRUST_BUILDING and state.relationship_level >= 0.6:
                ready = True
            elif state.current_step == ArcStep.CONFLICT and "conflict_resolved" in state.flags:
                ready = True
            elif state.current_step == ArcStep.RESOLUTION and state.relationship_level >= 0.8:
                ready = True
            
            if ready and current_idx < len(step_order) - 1:
                state.current_step = step_order[current_idx + 1]
                return True
        except ValueError:
            pass
        
        return False
    
    def set_flag(self, npc_id: str, flag: str) -> bool:
        """Set a flag for an NPC's arc."""
        state = self.arc_states.get(npc_id)
        if not state:
            return False
        
        state.flags.add(flag)
        
        # Check if this flag triggers arc advancement
        self.advance_arc(npc_id)
        return True
    
    def check_flag(self, npc_id: str, flag: str) -> bool:
        """Check if an NPC has a specific flag."""
        state = self.arc_states.get(npc_id)
        if not state:
            return False
        return flag in state.flags
    
    def modify_morale(
        self,
        npc_id: Optional[str] = None,
        delta: float = 0.0,
        affect_crew: bool = False
    ) -> None:
        """
        Modify morale for an NPC or the entire crew.
        
        Args:
            npc_id: Specific NPC to affect, or None for crew-wide
            delta: Change in morale (-1.0 to 1.0)
            affect_crew: If True, also affects crew morale
        """
        if npc_id:
            state = self.arc_states.get(npc_id)
            if state:
                state.morale = max(0.0, min(1.0, state.morale + delta))
                
                if affect_crew:
                    # Individual morale affects crew morale (weighted)
                    self.crew_morale = max(0.0, min(1.0, self.crew_morale + delta * 0.2))
        else:
            # Affect all NPCs
            for state in self.arc_states.values():
                state.morale = max(0.0, min(1.0, state.morale + delta))
            
            self.crew_morale = max(0.0, min(1.0, self.crew_morale + delta))
    
    def record_interaction(self, npc_id: str, moment_description: str = "") -> None:
        """Record an interaction with an NPC."""
        state = self.arc_states.get(npc_id)
        if not state:
            return
        
        state.interactions_count += 1
        
        if moment_description:
            state.key_moments.append(moment_description)
            # Keep only last 10 moments
            if len(state.key_moments) > 10:
                state.key_moments = state.key_moments[-10:]
        
        # Check for arc advancement
        self.advance_arc(npc_id)
    
    def sync_with_relationship_web(self, relationship_web: "RelationshipWeb") -> None:
        """
        Sync arc states with the relationship system.
        Updates relationship levels from trust values.
        """
        for npc_id, state in self.arc_states.items():
            crew_member = relationship_web.crew.get(npc_id)
            if crew_member:
                state.relationship_level = crew_member.trust
    
    def update_relationship_web(self, relationship_web: "RelationshipWeb") -> None:
        """
        Update relationship web from arc states.
        Pushes relationship levels back to trust values.
        """
        for npc_id, state in self.arc_states.items():
            crew_member = relationship_web.crew.get(npc_id)
            if crew_member:
                crew_member.trust = state.relationship_level
    
    def get_morale_status(self) -> dict:
        """Get morale status for all NPCs and crew."""
        return {
            "crew_morale": self.crew_morale,
            "individual_morale": {
                npc_id: state.morale
                for npc_id, state in self.arc_states.items()
            }
        }
    
    def get_arc_summary(self, npc_id: str) -> str:
        """Get a text summary of an NPC's arc state."""
        state = self.arc_states.get(npc_id)
        if not state:
            return f"No arc data for {npc_id}"
        
        lines = [
            f"=== {npc_id.upper()} ARC STATUS ===",
            f"Current Step: {state.current_step.value.replace('_', ' ').title()}",
            f"Relationship: {state.relationship_level:.0%}",
            f"Morale: {state.morale:.0%}",
            f"Interactions: {state.interactions_count}",
            f"Active Flags: {', '.join(state.flags) if state.flags else 'None'}",
        ]
        
        if state.key_moments:
            lines.append(f"Recent Moments:")
            for moment in state.key_moments[-3:]:
                lines.append(f"  - {moment}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Serialize arc manager state."""
        return {
            "crew_morale": self.crew_morale,
            "arc_states": {
                npc_id: state.to_dict()
                for npc_id, state in self.arc_states.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CampArcManager":
        """Deserialize arc manager state."""
        manager = cls()
        manager.crew_morale = data.get("crew_morale", 0.5)
        
        for npc_id, state_data in data.get("arc_states", {}).items():
            manager.arc_states[npc_id] = ArcState.from_dict(state_data)
        
        return manager


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_arc_manager() -> CampArcManager:
    """Create a new arc manager."""
    return CampArcManager()


def get_npcs_at_arc_step(manager: CampArcManager, step: ArcStep) -> list[str]:
    """Get all NPCs currently at a specific arc step."""
    return [
        npc_id
        for npc_id, state in manager.arc_states.items()
        if state.current_step == step
    ]


def get_low_morale_npcs(manager: CampArcManager, threshold: float = 0.3) -> list[str]:
    """Get NPCs with morale below threshold."""
    return [
        npc_id
        for npc_id, state in manager.arc_states.items()
        if state.morale < threshold
    ]
