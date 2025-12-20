"""
NPC Goal Pursuit System.

This module gives NPCs agency by assigning them goals and tracking their
progress, allowing them to take actions even when the player isn't looking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random

@dataclass
class NPCGoal:
    """A high-level objective for an NPC."""
    goal_id: str
    description: str
    steps: List[str]
    current_step_index: int = 0
    completed: bool = False
    
    @property
    def current_step(self) -> Optional[str]:
        if not self.completed and self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

@dataclass
class NPCGoalPursuitSystem:
    """
    Manages active goals for NPCs.
    """
    npc_goals: Dict[str, NPCGoal] = field(default_factory=dict) # npc_id -> Goal
    
    def set_goal(self, npc_id: str, description: str, steps: List[str]):
        """Give an NPC a new mission."""
        self.npc_goals[npc_id] = NPCGoal(
            goal_id=f"{npc_id}_goal",
            description=description,
            steps=steps
        )

    def advance_npc_goals(self, active_npcs_in_scene: List[str]) -> List[str]:
        """
        Simulate progress for NPCs NOT in the current scene (background simulation).
        Returns a list of "rumors" or visible effects of these off-screen actions.
        """
        updates = []
        
        for npc_id, goal in self.npc_goals.items():
            if goal.completed:
                continue
            
            # Simple simulation: 20% chance to advance a step if off-screen
            if npc_id not in active_npcs_in_scene:
                if random.random() < 0.2:
                    completed_step = goal.current_step
                    goal.current_step_index += 1
                    
                    if goal.current_step_index >= len(goal.steps):
                        goal.completed = True
                        updates.append(f"RUMOR: {npc_id} has finally {goal.description}.")
                    else:
                        updates.append(f"NEWS: {npc_id} was seen {completed_step}.")
                        
        return updates

    def get_npc_agenda(self, npc_id: str) -> Optional[str]:
        """Get the current thing this NPC is trying to do (for scene logic)."""
        if npc_id in self.npc_goals:
            goal = self.npc_goals[npc_id]
            if not goal.completed:
                return f"Current Objective: {goal.current_step} (Goal: {goal.description})"
        return None

    def to_dict(self) -> dict:
        return {
            "npc_goals": {
                nid: {
                    "goal_id": g.goal_id,
                    "description": g.description,
                    "steps": g.steps,
                    "current_step_index": g.current_step_index,
                    "completed": g.completed
                }
                for nid, g in self.npc_goals.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NPCGoalPursuitSystem":
        sys = cls()
        for nid, g_data in data.get("npc_goals", {}).items():
            sys.npc_goals[nid] = NPCGoal(
                goal_id=g_data["goal_id"],
                description=g_data["description"],
                steps=g_data["steps"],
                current_step_index=g_data["current_step_index"],
                completed=g_data["completed"]
            )
        return sys
