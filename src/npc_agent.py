from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from src.goap import GOAPPlanner, GOAPGoal, GOAPAction, WorldState, create_combat_planner

@dataclass
class NPCAgent:
    """
    An autonomous agent using GOAP.
    Manages state, goals, and planning.
    """
    id: str
    name: str
    planner: GOAPPlanner
    goals: list[GOAPGoal] = field(default_factory=list)
    state: WorldState = field(default_factory=lambda: WorldState())
    current_plan: list[GOAPAction] = field(default_factory=list)
    current_action: GOAPAction | None = None
    
    def update_perception(self, observation: dict[str, Any]) -> None:
        """Update internal world state based on observation."""
        for k, v in observation.items():
            self.state.set(k, v)
        
        # Verify current plan validity
        if self.current_plan:
             # Check if next action's preconditions are still met
             next_action = self.current_plan[0]
             if not next_action.is_valid(self.state):
                 # Plan broken
                 self.current_plan = []
    
    def get_next_action(self) -> dict | None:
        """
        Decide what to do next.
        Returns action dict or None (idle).
        """
        # 1. Check if current plan is empty/finished
        if not self.current_plan:
            # Re-plan
            goal, plan = self.planner.plan_for_best_goal(self.state, self.goals)
            if plan:
                self.current_plan = plan
            else:
                return None # No achievable goals
        
        # 2. Get next action
        if self.current_plan:
            action = self.current_plan[0]
            
            # 3. Check preconditions (double check)
            if action.is_valid(self.state):
                # 4. Remove from queue (assuming success)
                self.current_plan.pop(0)
                
                # Apply predicted effects immediately to internal state
                self.state = action.apply(self.state)
                
                return {
                    "name": action.name,
                    "description": f"{self.name} {action.description}",
                    "effect": action.effects
                }
            else:
                # Plan invalid, clear it
                self.current_plan = []
                return None
        
        return None

def create_combat_agent(id: str, name: str) -> NPCAgent:
    """Create a standard combat agent."""
    planner = create_combat_planner()
    
    # Define Goals
    kill_player = GOAPGoal(
        name="kill_player",
        conditions={"target_damaged": True},
        priority=2.0
    )
    survive = GOAPGoal(
        name="survive",
        conditions={"escaped": True},
        priority=5.0,
        relevance_check=lambda s: s.get("health", 1.0) < 0.3
    )
    
    agent = NPCAgent(
        id=id,
        name=name,
        planner=planner,
        goals=[kill_player, survive],
        state=WorldState(facts={
            "has_weapon": True,
            "weapon_drawn": False,
            "target_in_range": False,
            "target_visible": True,
            "health": 1.0,
            "ammo_loaded": True
        })
    )
    return agent
