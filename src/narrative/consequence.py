"""
Consequence Escalation Chains.

This module implements systems where small player choices snowball into 
larger crises over time through defined escalation stages.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import uuid

@dataclass
class EscalationStage:
    """A single stage in a consequence chain."""
    stage_id: int
    delay_scenes: int  # Scenes to wait after previous stage
    event_description: str
    severity: float = 0.5  # 0.0 to 1.0

@dataclass
class ActiveChain:
    """A chain currently progressing in the game."""
    chain_id: str
    initial_choice_desc: str
    initial_scene: int
    stages: List[EscalationStage]
    current_stage_index: int = -1  # -1 means chain started but no stage triggered yet
    last_trigger_scene: int = 0  # Scene number when the last event fired
    
    @property
    def is_complete(self) -> bool:
        return self.current_stage_index >= len(self.stages) - 1

@dataclass
class ConsequenceManager:
    """
    Manages active consequence chains.
    """
    active_chains: Dict[str, ActiveChain] = field(default_factory=dict)
    
    def start_chain(self, choice_desc: str, current_scene: int, stages: List[EscalationStage]) -> str:
        """
        Start a new consequence chain based on a player choice.
        """
        chain_id = str(uuid.uuid4())
        chain = ActiveChain(
            chain_id=chain_id,
            initial_choice_desc=choice_desc,
            initial_scene=current_scene,
            stages=stages,
            last_trigger_scene=current_scene 
        )
        self.active_chains[chain_id] = chain
        return chain_id

    def check_progression(self, current_scene: int) -> List[Dict[str, Any]]:
        """
        Check all active chains to see if next stage should trigger.
        Returns list of events to trigger now.
        """
        triggered_events = []
        
        for chain in self.active_chains.values():
            if chain.is_complete:
                continue
                
            next_stage_idx = chain.current_stage_index + 1
            if next_stage_idx < len(chain.stages):
                next_stage = chain.stages[next_stage_idx]
                
                # Check if enough time has passed since last trigger (or start)
                scenes_passed = current_scene - chain.last_trigger_scene
                
                if scenes_passed >= next_stage.delay_scenes:
                    # Trigger this stage
                    chain.current_stage_index = next_stage_idx
                    chain.last_trigger_scene = current_scene
                    
                    triggered_events.append({
                        "chain_id": chain.chain_id,
                        "cause": chain.initial_choice_desc,
                        "event": next_stage.event_description,
                        "severity": next_stage.severity,
                        "stage_index": next_stage_idx,
                        "total_stages": len(chain.stages)
                    })
                    
        return triggered_events

    def to_dict(self) -> dict:
        """Serialize state."""
        return {
            "active_chains": {
                cid: {
                    "chain_id": c.chain_id,
                    "initial_choice_desc": c.initial_choice_desc,
                    "initial_scene": c.initial_scene,
                    "current_stage_index": c.current_stage_index,
                    "last_trigger_scene": c.last_trigger_scene,
                    "stages": [
                        {
                            "stage_id": s.stage_id,
                            "delay_scenes": s.delay_scenes,
                            "event_description": s.event_description,
                            "severity": s.severity
                        } for s in c.stages
                    ]
                }
                for cid, c in self.active_chains.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConsequenceManager":
        """Deserialize state."""
        manager = cls()
        chains_data = data.get("active_chains", {})
        
        for cid, c_data in chains_data.items():
            stages = [
                EscalationStage(
                    stage_id=s["stage_id"],
                    delay_scenes=s["delay_scenes"],
                    event_description=s["event_description"],
                    severity=s.get("severity", 0.5)
                ) for s in c_data.get("stages", [])
            ]
            
            chain = ActiveChain(
                chain_id=c_data["chain_id"],
                initial_choice_desc=c_data["initial_choice_desc"],
                initial_scene=c_data["initial_scene"],
                stages=stages,
                current_stage_index=c_data["current_stage_index"],
                last_trigger_scene=c_data["last_trigger_scene"]
            )
            manager.active_chains[cid] = chain
            
        return manager
