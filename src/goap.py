"""
Goal-Oriented Action Planning (GOAP) System.
Allows NPCs to dynamically generate plans to achieve goals.

Based on GOAP as pioneered in F.E.A.R. and used in many AAA titles.
Uses backward chaining from goal state to find valid action sequences.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
from heapq import heappush, heappop
from collections import deque


# ============================================================================
# World State
# ============================================================================

@dataclass
class WorldState:
    """
    Represents the current state of the world as key-value pairs.
    Used for preconditions and effects.
    """
    facts: dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.facts.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self.facts[key] = value
    
    def copy(self) -> "WorldState":
        return WorldState(facts=self.facts.copy())
    
    def satisfies(self, conditions: dict[str, Any]) -> bool:
        """Check if this state satisfies all given conditions."""
        for key, required_value in conditions.items():
            if self.facts.get(key) != required_value:
                return False
        return True
    
    def difference(self, goal: dict[str, Any]) -> dict[str, Any]:
        """Get conditions from goal that aren't satisfied."""
        unsatisfied = {}
        for key, value in goal.items():
            if self.facts.get(key) != value:
                unsatisfied[key] = value
        return unsatisfied
    
    def apply_effects(self, effects: dict[str, Any], pool: "WorldStatePool | None" = None) -> "WorldState":
        """Apply effects and return new state, optionally using a pool."""

        if pool:
            new_state = pool.clone(self, effects)
        else:
            new_state = self.copy()
            for key, value in effects.items():
                new_state.facts[key] = value
        return new_state


class WorldStatePool:
    """Reusable pool for ``WorldState`` instances to limit allocations."""

    def __init__(self) -> None:
        self._pool: deque[WorldState] = deque()
        self._leased: list[WorldState] = []

    def clone(self, base: WorldState, effects: dict[str, Any] | None = None) -> WorldState:
        state = self._pool.pop() if self._pool else WorldState()
        state.facts.clear()
        state.facts.update(base.facts)
        if effects:
            state.facts.update(effects)
        self._leased.append(state)
        return state

    def recycle(self) -> None:
        if self._leased:
            self._pool.extend(self._leased)
            self._leased.clear()


# ============================================================================
# Actions
# ============================================================================

@dataclass
class GOAPAction:
    """
    An action that can be taken to change world state.
    
    Preconditions must be satisfied for action to be valid.
    Effects are applied when action completes.
    """
    name: str
    cost: float = 1.0  # Lower = preferred
    
    # What must be true to perform this action
    preconditions: dict[str, Any] = field(default_factory=dict)
    
    # What becomes true after performing this action
    effects: dict[str, Any] = field(default_factory=dict)
    
    # Narrative context
    description: str = ""
    animation: str = ""  # For game integration
    
    # Dynamic cost modifier (optional)
    cost_modifier: Callable[[WorldState], float] | None = None
    
    def is_valid(self, state: WorldState) -> bool:
        """Check if this action can be performed in current state."""
        return state.satisfies(self.preconditions)
    
    def get_cost(self, state: WorldState) -> float:
        """Get the cost, optionally modified by world state."""
        base_cost = self.cost
        if self.cost_modifier:
            base_cost *= self.cost_modifier(state)
        return max(0.1, base_cost)
    
    def apply(self, state: WorldState, pool: WorldStatePool | None = None) -> WorldState:
        """Apply this action's effects to the state."""

        return state.apply_effects(self.effects, pool=pool)


# ============================================================================
# Goals
# ============================================================================

@dataclass
class GOAPGoal:
    """
    A goal the NPC wants to achieve.
    Defined as a set of world state conditions.
    """
    name: str
    conditions: dict[str, Any] = field(default_factory=dict)
    priority: float = 1.0  # Higher = more important
    
    # When to consider this goal
    relevance_check: Callable[[WorldState], bool] | None = None
    
    def is_satisfied(self, state: WorldState) -> bool:
        """Check if goal is achieved in current state."""
        return state.satisfies(self.conditions)
    
    def is_relevant(self, state: WorldState) -> bool:
        """Check if this goal should be considered right now."""
        if self.relevance_check:
            return self.relevance_check(state)
        # If goal is already satisfied, it's not relevant
        return not self.is_satisfied(state)


# ============================================================================
# Planner
# ============================================================================

@dataclass
class PlanNode:
    """A node in the planning search tree."""
    state: WorldState
    actions: list[GOAPAction]
    cost: float
    
    def __lt__(self, other):
        return self.cost < other.cost


class GOAPPlanner:
    """
    Plans action sequences to achieve goals using backward chaining.
    Uses A* search to find lowest-cost valid plan.
    """

    def __init__(
        self,
        available_actions: list[GOAPAction],
        *,
        action_heuristic=None,
        decision_log: list[str] | None = None,
    ):
        self.actions = available_actions
        self.max_depth = 10
        self.max_iterations = 1000
        self.action_heuristic = action_heuristic
        self.decision_log = decision_log
        self._state_pool = WorldStatePool()
    
    def plan(
        self,
        start_state: WorldState,
        goal: GOAPGoal,
    ) -> list[GOAPAction] | None:
        """
        Find a sequence of actions to achieve the goal.
        
        Args:
            start_state: Current world state
            goal: Goal to achieve
            
        Returns:
            List of actions to perform, or None if no plan found
        """
        # Return states from previous runs so they can be reused.
        self._state_pool.recycle()

        if goal.is_satisfied(start_state):
            return []  # Already achieved

        # A* search
        open_set: list[PlanNode] = []
        initial_state = self._state_pool.clone(start_state)
        heappush(open_set, PlanNode(
            state=initial_state,
            actions=[],
            cost=0,
        ))
        
        visited: set[tuple] = set()
        iterations = 0
        
        while open_set and iterations < self.max_iterations:
            iterations += 1
            current = heappop(open_set)
            
            # Check if we've reached the goal
            if goal.is_satisfied(current.state):
                self._state_pool.recycle()
                return current.actions
            
            # Check depth limit
            if len(current.actions) >= self.max_depth:
                continue
            
            # Create state signature for visited check
            state_sig = tuple(sorted(current.state.facts.items()))
            if state_sig in visited:
                continue
            visited.add(state_sig)
            
            # Try each action
            for action in self.actions:
                if action.is_valid(current.state):
                    new_state = action.apply(current.state)
                    action_cost = action.get_cost(current.state)

                    heuristic_bonus = 0.0
                    heuristic_reason = ""
                    if self.action_heuristic:
                        heuristic_bonus, heuristic_reason = self.action_heuristic(action, current.state)
                        if heuristic_bonus:
                            action_cost *= max(0.2, 1.0 - heuristic_bonus)
                    if self.decision_log is not None and heuristic_reason:
                        self.decision_log.append(
                            f"{action.name}: {heuristic_reason} (bonus={heuristic_bonus:.2f})"
                        )

                    new_cost = current.cost + action_cost
                    
                    new_state = action.apply(current.state, pool=self._state_pool)
                    new_cost = current.cost + action.get_cost(current.state)

                    # Heuristic: unsatisfied goal conditions
                    h_cost = len(new_state.difference(goal.conditions)) * 0.5

                    heappush(open_set, PlanNode(
                        state=new_state,
                        actions=current.actions + [action],
                        cost=new_cost + h_cost,
                    ))

        self._state_pool.recycle()
        return None  # No plan found
    
    def plan_for_best_goal(
        self,
        start_state: WorldState,
        goals: list[GOAPGoal],
    ) -> tuple[GOAPGoal | None, list[GOAPAction]]:
        """
        Find a plan for the highest-priority achievable goal.
        
        Returns:
            Tuple of (selected_goal, action_list)
        """
        # Sort goals by priority
        relevant_goals = [g for g in goals if g.is_relevant(start_state)]
        relevant_goals.sort(key=lambda g: g.priority, reverse=True)
        
        for goal in relevant_goals:
            plan = self.plan(start_state, goal)
            if plan is not None:
                return goal, plan
        
        return None, []


# ============================================================================
# Pre-built Action Libraries
# ============================================================================

# Combat actions
COMBAT_ACTIONS = [
    GOAPAction(
        name="draw_weapon",
        cost=1.0,
        preconditions={"has_weapon": True, "weapon_drawn": False},
        effects={"weapon_drawn": True},
        description="draws their weapon",
    ),
    GOAPAction(
        name="attack",
        cost=2.0,
        preconditions={"weapon_drawn": True, "target_in_range": True},
        effects={"target_damaged": True},
        description="attacks the target",
    ),
    GOAPAction(
        name="move_to_target",
        cost=3.0,
        preconditions={"target_visible": True},
        effects={"target_in_range": True},
        description="closes the distance",
    ),
    GOAPAction(
        name="find_target",
        cost=4.0,
        preconditions={},
        effects={"target_visible": True, "target_in_range": False},
        description="searches for the target",
    ),
    GOAPAction(
        name="reload",
        cost=2.0,
        preconditions={"has_ammo": True, "ammo_loaded": False},
        effects={"ammo_loaded": True},
        description="reloads their weapon",
    ),
    GOAPAction(
        name="take_cover",
        cost=2.0,
        preconditions={"has_cover": True, "in_cover": False},
        effects={"in_cover": True},
        description="takes cover",
    ),
    GOAPAction(
        name="regroup",
        cost=2.2,
        preconditions={"has_allies": True},
        effects={"grouped_up": True, "in_cover": True},
        description="falls back toward allies and stabilizes",
    ),
    GOAPAction(
        name="flee",
        cost=5.0,
        preconditions={},
        effects={"escaped": True, "target_in_range": False},
        description="flees from combat",
    ),
]

# Resource gathering actions
RESOURCE_ACTIONS = [
    GOAPAction(
        name="gather_wood",
        cost=3.0,
        preconditions={"near_trees": True},
        effects={"has_wood": True},
        description="gathers wood from nearby trees",
    ),
    GOAPAction(
        name="mine_iron",
        cost=4.0,
        preconditions={"near_ore": True, "has_pickaxe": True},
        effects={"has_iron": True},
        description="mines iron ore",
    ),
    GOAPAction(
        name="craft_axe",
        cost=2.0,
        preconditions={"has_wood": True, "has_iron": True},
        effects={"has_axe": True, "has_wood": False, "has_iron": False},
        description="crafts an axe",
    ),
    GOAPAction(
        name="craft_pickaxe",
        cost=2.0,
        preconditions={"has_wood": True, "has_iron": True},
        effects={"has_pickaxe": True, "has_wood": False, "has_iron": False},
        description="crafts a pickaxe",
    ),
    GOAPAction(
        name="go_to_forest",
        cost=3.0,
        preconditions={},
        effects={"near_trees": True, "near_ore": False},
        description="travels to the forest",
    ),
    GOAPAction(
        name="go_to_mine",
        cost=3.0,
        preconditions={},
        effects={"near_ore": True, "near_trees": False},
        description="travels to the mine",
    ),
]

# Social actions
SOCIAL_ACTIONS = [
    GOAPAction(
        name="greet",
        cost=1.0,
        preconditions={"target_nearby": True},
        effects={"conversation_started": True},
        description="greets the player",
    ),
    GOAPAction(
        name="offer_quest",
        cost=2.0,
        preconditions={"conversation_started": True, "has_quest": True},
        effects={"quest_offered": True},
        description="offers a task",
    ),
    GOAPAction(
        name="trade",
        cost=2.0,
        preconditions={"conversation_started": True, "has_goods": True},
        effects={"trade_complete": True},
        description="opens trade",
    ),
    GOAPAction(
        name="warn_danger",
        cost=1.5,
        preconditions={"knows_danger": True, "target_nearby": True},
        effects={"target_warned": True},
        description="warns about danger ahead",
    ),
]


# ============================================================================
# Convenience Functions
# ============================================================================

def create_combat_planner(
    *, action_heuristic=None, decision_log: list[str] | None = None
) -> GOAPPlanner:
    """Create a planner with combat actions and optional heuristics."""

    return GOAPPlanner(
        COMBAT_ACTIONS,
        action_heuristic=action_heuristic,
        decision_log=decision_log,
    )


def create_resource_planner() -> GOAPPlanner:
    """Create a planner with resource gathering actions."""
    return GOAPPlanner(RESOURCE_ACTIONS)


def create_social_planner() -> GOAPPlanner:
    """Create a planner with social actions."""
    return GOAPPlanner(SOCIAL_ACTIONS)


def plan_npc_action(
    goal_name: str,
    goal_conditions: dict[str, Any],
    current_state: dict[str, Any],
    action_type: str = "combat",
    *,
    action_heuristic=None,
    decision_log: list[str] | None = None,
) -> list[dict]:
    """
    Quick function to plan NPC actions.
    
    Args:
        goal_name: Name of what NPC wants to achieve
        goal_conditions: What must be true when goal is achieved
        current_state: Current world state
        action_type: "combat", "resource", or "social"
        
    Returns:
        List of action dicts with name and description
    """
    # Select planner
    if action_type == "combat":
        planner = create_combat_planner(
            action_heuristic=action_heuristic, decision_log=decision_log
        )
    elif action_type == "resource":
        planner = create_resource_planner()
    else:
        planner = create_social_planner()
    
    # Create state and goal
    state = WorldState(facts=current_state)
    goal = GOAPGoal(name=goal_name, conditions=goal_conditions)
    
    # Plan
    plan = planner.plan(state, goal)
    
    if plan is None:
        return []
    
    return [{"name": a.name, "description": a.description} for a in plan]


def get_plan_narrative(plan: list[GOAPAction]) -> str:
    """Generate narrative context from a plan."""
    if not plan:
        return ""
    
    lines = ["[NPC PLAN]"]
    for i, action in enumerate(plan, 1):
        lines.append(f"{i}. {action.description.capitalize()}")
    
    return "\n".join(lines)
