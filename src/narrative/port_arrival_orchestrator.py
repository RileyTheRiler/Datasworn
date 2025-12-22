"""
Port Arrival Orchestrator

Manages the progression through the Port Arrival sequence and tracks state.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from src.narrative.port_arrival import (
    PortArrivalStage,
    DockingScenario,
    get_approach_scene,
    get_docking_scene,
    get_npc_dispersal,
    get_all_dispersals,
    get_epilogue
)
from src.character_identity import WoundType


@dataclass
class PortArrivalState:
    """Tracks the current state of the Port Arrival sequence."""
    current_stage: PortArrivalStage = PortArrivalStage.APPROACH
    completed_npc_conversations: List[str] = field(default_factory=list)
    docking_scenario: Optional[DockingScenario] = None
    dispersal_viewed: List[str] = field(default_factory=list)
    epilogue_viewed: bool = False
    
    def to_dict(self) -> dict:
        """Serialize state to dict."""
        return {
            "current_stage": self.current_stage.value,
            "completed_npc_conversations": self.completed_npc_conversations,
            "docking_scenario": self.docking_scenario.value if self.docking_scenario else None,
            "dispersal_viewed": self.dispersal_viewed,
            "epilogue_viewed": self.epilogue_viewed
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PortArrivalState":
        """Deserialize state from dict."""
        return cls(
            current_stage=PortArrivalStage(data.get("current_stage", "approach")),
            completed_npc_conversations=data.get("completed_npc_conversations", []),
            docking_scenario=DockingScenario(data["docking_scenario"]) if data.get("docking_scenario") else None,
            dispersal_viewed=data.get("dispersal_viewed", []),
            epilogue_viewed=data.get("epilogue_viewed", False)
        )


class PortArrivalOrchestrator:
    """Orchestrates the Port Arrival sequence progression."""
    
    def __init__(self, state: Optional[PortArrivalState] = None):
        self.state = state or PortArrivalState()
    
    def get_approach(self, npc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Day 8 approach scene content.
        
        Args:
            npc_id: Optional specific NPC conversation
            
        Returns:
            Approach scene content
        """
        scene = get_approach_scene(npc_id)
        
        # Track completed conversations
        if npc_id and "error" not in scene:
            if npc_id not in self.state.completed_npc_conversations:
                self.state.completed_npc_conversations.append(npc_id)
        
        return scene
    
    def get_docking(self, story_choices: Dict[str, bool]) -> Dict[str, Any]:
        """
        Get docking scenario based on story choices.
        
        Args:
            story_choices: Dict with story state flags
            
        Returns:
            Docking scene content
        """
        scene = get_docking_scene(story_choices)
        
        # Update state
        if "scenario" in scene:
            self.state.docking_scenario = DockingScenario(scene["scenario"])
            self.state.current_stage = PortArrivalStage.DOCKING
        
        return scene
    
    def get_dispersal(self, ending_type: str, npc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get NPC dispersal outcomes.
        
        Args:
            ending_type: 'hero' or 'tragedy'
            npc_id: Optional specific NPC
            
        Returns:
            Dispersal content
        """
        if npc_id:
            dispersal = get_npc_dispersal(npc_id, ending_type)
            
            # Track viewed dispersals
            if "error" not in dispersal and npc_id not in self.state.dispersal_viewed:
                self.state.dispersal_viewed.append(npc_id)
        else:
            dispersal = get_all_dispersals(ending_type)
        
        # Update stage
        self.state.current_stage = PortArrivalStage.DISPERSAL
        
        return dispersal
    
    def get_epilogue_content(self, archetype: WoundType, ending_type: str) -> Dict[str, Any]:
        """
        Get epilogue for the player's archetype and ending path.
        
        Args:
            archetype: Player's WoundType
            ending_type: 'hero' or 'tragedy'
            
        Returns:
            Epilogue content
        """
        epilogue = get_epilogue(archetype, ending_type)
        
        # Update state
        self.state.epilogue_viewed = True
        self.state.current_stage = PortArrivalStage.EPILOGUE
        
        return epilogue
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current port arrival progress.
        
        Returns:
            Status information
        """
        return {
            "current_stage": self.state.current_stage.value,
            "completed_conversations": self.state.completed_npc_conversations,
            "available_conversations": ["torres", "kai", "okonkwo", "vasquez", "ember"],
            "remaining_conversations": [
                npc for npc in ["torres", "kai", "okonkwo", "vasquez", "ember"]
                if npc not in self.state.completed_npc_conversations
            ],
            "docking_scenario": self.state.docking_scenario.value if self.state.docking_scenario else None,
            "dispersal_viewed": self.state.dispersal_viewed,
            "epilogue_viewed": self.state.epilogue_viewed
        }
    
    def to_dict(self) -> dict:
        """Serialize orchestrator to dict."""
        return {
            "state": self.state.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PortArrivalOrchestrator":
        """Deserialize orchestrator from dict."""
        state = PortArrivalState.from_dict(data.get("state", {}))
        return cls(state=state)
