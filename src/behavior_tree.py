"""
Behavior Tree System for NPC Decision Making.
Provides a modular framework for defining complex NPC behaviors.

Based on Game AI Pro patterns for hierarchical task organization.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


# ============================================================================
# Node Status
# ============================================================================

class NodeStatus(Enum):
    """Result of a behavior tree node execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"


# ============================================================================
# Base Node Classes
# ============================================================================

@dataclass
class BTContext:
    """
    Blackboard-style context passed through the behavior tree.
    Contains all data an NPC needs to make decisions.
    """
    # NPC identity
    npc_id: str = ""
    npc_name: str = ""
    archetype: str = ""
    
    # World awareness
    player_name: str = ""
    player_reputation: float = 0.5  # 0=hated, 1=trusted
    faction_reputation: float = 0.0
    npc_reputation: float = 0.0
    player_nearby: bool = True
    current_location: str = ""
    
    # NPC state
    health: float = 1.0  # 0-1
    disposition: float = 0.5  # 0=hostile, 1=friendly
    has_quest: bool = False
    quest_name: str = ""
    in_combat: bool = False
    is_alerted: bool = False
    
    # Combat state
    threat_level: float = 0.0  # 0-1
    allies_nearby: int = 0
    has_cover: bool = False
    ammo: float = 1.0  # 0-1
    
    # Memory/knowledge
    last_seen_player: str = ""  # Location where player was last seen
    knows_player_reputation: bool = True
    rumors_heard: list[str] = field(default_factory=list)
    recent_memory_flags: list[str] = field(default_factory=list)
    memory_summary: str = ""
    
    # Output - set by leaf nodes
    action: str = ""
    dialogue_intent: str = ""
    movement_target: str = ""


class BTNode(ABC):
    """Abstract base class for all behavior tree nodes."""
    
    @abstractmethod
    def execute(self, context: BTContext) -> NodeStatus:
        """Execute this node and return its status."""
        pass
    
    @property
    def name(self) -> str:
        return self.__class__.__name__


# ============================================================================
# Composite Nodes
# ============================================================================

class Sequence(BTNode):
    """
    Executes children in order. Fails if any child fails.
    Like an AND gate - all must succeed.
    """
    
    def __init__(self, *children: BTNode, name: str = ""):
        self.children = list(children)
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name or "Sequence"
    
    def execute(self, context: BTContext) -> NodeStatus:
        for child in self.children:
            status = child.execute(context)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS


class Selector(BTNode):
    """
    Tries children in order until one succeeds.
    Like an OR gate - any success is enough.
    """
    
    def __init__(self, *children: BTNode, name: str = ""):
        self.children = list(children)
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name or "Selector"
    
    def execute(self, context: BTContext) -> NodeStatus:
        for child in self.children:
            status = child.execute(context)
            if status == NodeStatus.SUCCESS:
                return status
            if status == NodeStatus.RUNNING:
                return status
        return NodeStatus.FAILURE


class Parallel(BTNode):
    """
    Executes all children simultaneously.
    Succeeds if enough children succeed.
    """
    
    def __init__(self, *children: BTNode, required_successes: int = 1, name: str = ""):
        self.children = list(children)
        self.required_successes = required_successes
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name or "Parallel"
    
    def execute(self, context: BTContext) -> NodeStatus:
        successes = 0
        for child in self.children:
            status = child.execute(context)
            if status == NodeStatus.SUCCESS:
                successes += 1
        
        if successes >= self.required_successes:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE


# ============================================================================
# Decorator Nodes
# ============================================================================

class Inverter(BTNode):
    """Inverts the result of its child (SUCCESS <-> FAILURE)."""
    
    def __init__(self, child: BTNode):
        self.child = child
    
    def execute(self, context: BTContext) -> NodeStatus:
        status = self.child.execute(context)
        if status == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        if status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        return status  # RUNNING stays RUNNING


class Repeater(BTNode):
    """Repeats child a fixed number of times."""
    
    def __init__(self, child: BTNode, times: int = 1):
        self.child = child
        self.times = times
    
    def execute(self, context: BTContext) -> NodeStatus:
        for _ in range(self.times):
            status = self.child.execute(context)
            if status == NodeStatus.FAILURE:
                return NodeStatus.FAILURE
        return NodeStatus.SUCCESS


class Succeeder(BTNode):
    """Always returns SUCCESS, regardless of child result."""
    
    def __init__(self, child: BTNode):
        self.child = child
    
    def execute(self, context: BTContext) -> NodeStatus:
        self.child.execute(context)
        return NodeStatus.SUCCESS


# ============================================================================
# Condition Nodes (Leaf nodes that check state)
# ============================================================================

class Condition(BTNode):
    """Generic condition check using a lambda."""
    
    def __init__(self, check: Callable[[BTContext], bool], name: str = "Condition"):
        self.check = check
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if self.check(context) else NodeStatus.FAILURE


# Pre-built conditions
class IsPlayerNearby(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if context.player_nearby else NodeStatus.FAILURE


class IsHostile(BTNode):
    """Check if NPC should be hostile based on disposition."""
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
    
    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if context.disposition < self.threshold else NodeStatus.FAILURE


class IsFriendly(BTNode):
    """Check if NPC should be friendly based on disposition."""
    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold
    
    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if context.disposition >= self.threshold else NodeStatus.FAILURE


class HasQuest(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if context.has_quest else NodeStatus.FAILURE


class InCombat(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if context.in_combat else NodeStatus.FAILURE


class IsHealthLow(BTNode):
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
    
    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if context.health < self.threshold else NodeStatus.FAILURE


class IsThreatHigh(BTNode):
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
    
    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if context.threat_level > self.threshold else NodeStatus.FAILURE


class HasAllies(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if context.allies_nearby > 0 else NodeStatus.FAILURE


class ReputationThreshold(BTNode):
    """Gate behavior by reputation scores."""

    def __init__(self, npc_threshold: float = 0.0, faction_threshold: float = 0.0):
        self.npc_threshold = npc_threshold
        self.faction_threshold = faction_threshold

    def execute(self, context: BTContext) -> NodeStatus:
        npc_ok = context.npc_reputation >= self.npc_threshold
        faction_ok = context.faction_reputation >= self.faction_threshold
        return NodeStatus.SUCCESS if (npc_ok and faction_ok) else NodeStatus.FAILURE


class MemoryFlagPresent(BTNode):
    """Check if a remembered flag exists (e.g., promise broken)."""

    def __init__(self, flag: str):
        self.flag = flag

    def execute(self, context: BTContext) -> NodeStatus:
        return NodeStatus.SUCCESS if self.flag in context.recent_memory_flags else NodeStatus.FAILURE


# ============================================================================
# Action Nodes (Leaf nodes that do things)
# ============================================================================

class Action(BTNode):
    """Generic action using a lambda."""
    
    def __init__(self, action: Callable[[BTContext], bool], name: str = "Action"):
        self.action = action
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    def execute(self, context: BTContext) -> NodeStatus:
        result = self.action(context)
        return NodeStatus.SUCCESS if result else NodeStatus.FAILURE


# Pre-built actions
class SetAction(BTNode):
    """Set the action field in context."""
    
    def __init__(self, action_name: str):
        self.action_name = action_name
    
    def execute(self, context: BTContext) -> NodeStatus:
        context.action = self.action_name
        return NodeStatus.SUCCESS


class SetDialogueIntent(BTNode):
    """Set the dialogue intent for the narrator."""
    
    def __init__(self, intent: str):
        self.intent = intent
    
    def execute(self, context: BTContext) -> NodeStatus:
        context.dialogue_intent = self.intent
        return NodeStatus.SUCCESS


class Attack(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        context.action = "attack"
        context.dialogue_intent = "aggressive, threatening"
        return NodeStatus.SUCCESS


class Flee(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        context.action = "flee"
        context.dialogue_intent = "panicked, desperate"
        return NodeStatus.SUCCESS


class TakeCover(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        context.action = "take_cover"
        context.dialogue_intent = "tactical, cautious"
        return NodeStatus.SUCCESS


class OfferQuest(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        context.action = "offer_quest"
        context.dialogue_intent = f"has work for the player: {context.quest_name}"
        return NodeStatus.SUCCESS


class Greet(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        context.action = "greet"
        context.dialogue_intent = "friendly greeting"
        return NodeStatus.SUCCESS


class RecallRecentMemory(BTNode):
    """Inject memory summary into dialogue intent."""

    def __init__(self, fallback: str = "reflects on past dealings"):
        self.fallback = fallback

    def execute(self, context: BTContext) -> NodeStatus:
        summary = context.memory_summary or self.fallback
        context.dialogue_intent = f"references history: {summary}"
        return NodeStatus.SUCCESS


class Ignore(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        context.action = "ignore"
        context.dialogue_intent = "dismissive, uninterested"
        return NodeStatus.SUCCESS


class Warn(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        context.action = "warn"
        context.dialogue_intent = "cautious warning, not yet hostile"
        return NodeStatus.SUCCESS


class CallForHelp(BTNode):
    def execute(self, context: BTContext) -> NodeStatus:
        context.action = "call_for_help"
        context.dialogue_intent = "shouting for allies"
        return NodeStatus.SUCCESS


# ============================================================================
# Pre-built Behavior Trees for Archetypes
# ============================================================================

def create_merchant_tree() -> BTNode:
    """Behavior tree for merchant/trader NPCs."""
    return Selector(
        # Remember broken promises
        Sequence(
            MemoryFlagPresent("promise_broken"),
            RecallRecentMemory("demands restitution before trading"),
            SetAction("refuse_service"),
        ),
        # If hostile, refuse service
        Sequence(
            IsHostile(threshold=0.2),
            SetDialogueIntent("refuses to deal with the player"),
            SetAction("refuse_service"),
        ),
        # If has quest to offer
        Sequence(
            HasQuest(),
            IsFriendly(threshold=0.4),
            OfferQuest(),
        ),
        # Default: offer trade
        Sequence(
            ReputationThreshold(npc_threshold=0.1, faction_threshold=-0.2),
            IsPlayerNearby(),
            IsFriendly(threshold=0.3),
            SetDialogueIntent("offers goods and services"),
            SetAction("offer_trade"),
        ),
        # Neutral: brief acknowledgment
        Sequence(
            IsPlayerNearby(),
            Greet(),
        ),
        # Ignore if player not nearby
        Ignore(),
        name="MerchantBehavior"
    )


def create_guard_tree() -> BTNode:
    """Behavior tree for guard/security NPCs."""
    return Selector(
        # Combat behavior
        Sequence(
            InCombat(),
            Selector(
                # Low health - call for help or flee
                Sequence(
                    IsHealthLow(threshold=0.25),
                    Selector(
                        Sequence(HasAllies(), CallForHelp()),
                        Flee(),
                    ),
                ),
                # High threat - take cover
                Sequence(
                    IsThreatHigh(threshold=0.7),
                    TakeCover(),
                ),
                # Default combat - attack
                Attack(),
            ),
            name="GuardCombat"
        ),
        # Holds grudges from memory flags
        Sequence(
            MemoryFlagPresent("violent_history"),
            Warn(),
        ),
        # Suspicious of hostile player
        Sequence(
            IsHostile(threshold=0.3),
            Warn(),
        ),
        # React to low reputation with faction
        Sequence(
            ReputationThreshold(npc_threshold=-0.3, faction_threshold=-0.2),
            SetDialogueIntent("keeps hand on weapon due to reputation"),
            SetAction("observe"),
        ),
        # Quest offering for friendly players
        Sequence(
            HasQuest(),
            IsFriendly(threshold=0.5),
            OfferQuest(),
        ),
        # Patrol acknowledgment
        Sequence(
            IsPlayerNearby(),
            SetDialogueIntent("nods professionally"),
            SetAction("acknowledge"),
        ),
        # Default patrol
        SetAction("patrol"),
        name="GuardBehavior"
    )


def create_hostile_tree() -> BTNode:
    """Behavior tree for hostile/enemy NPCs."""
    return Selector(
        # Combat priority
        Sequence(
            InCombat(),
            Selector(
                # Critical health - flee
                Sequence(
                    IsHealthLow(threshold=0.15),
                    Flee(),
                ),
                # Low health with allies - take cover
                Sequence(
                    IsHealthLow(threshold=0.4),
                    HasAllies(),
                    TakeCover(),
                ),
                # High threat - tactical retreat
                Sequence(
                    IsThreatHigh(threshold=0.8),
                    Inverter(HasAllies()),
                    TakeCover(),
                ),
                # Attack
                Attack(),
            ),
        ),
        # If player nearby and not in combat - attack
        Sequence(
            IsPlayerNearby(),
            SetDialogueIntent("snarls and attacks"),
            Attack(),
        ),
        # Patrol/search
        SetAction("search_for_targets"),
        name="HostileBehavior"
    )


def create_civilian_tree() -> BTNode:
    """Behavior tree for civilian/non-combatant NPCs."""
    return Selector(
        # Flee from combat
        Sequence(
            InCombat(),
            Flee(),
        ),
        # Flee from hostiles
        Sequence(
            IsThreatHigh(threshold=0.5),
            Flee(),
        ),
        # Quest for friendly players
        Sequence(
            HasQuest(),
            IsFriendly(threshold=0.4),
            OfferQuest(),
        ),
        # Friendly greeting
        Sequence(
            IsPlayerNearby(),
            IsFriendly(threshold=0.5),
            Greet(),
        ),
        # Wary of unknown player
        Sequence(
            IsPlayerNearby(),
            SetDialogueIntent("watches warily"),
            SetAction("observe"),
        ),
        # Go about business
        SetAction("daily_routine"),
        name="CivilianBehavior"
    )


# ============================================================================
# Archetype Registry
# ============================================================================

ARCHETYPE_TREES: dict[str, Callable[[], BTNode]] = {
    "merchant": create_merchant_tree,
    "pragmatic_merchant": create_merchant_tree,
    "guard": create_guard_tree,
    "gruff_veteran": create_guard_tree,
    "hostile": create_hostile_tree,
    "raider": create_hostile_tree,
    "civilian": create_civilian_tree,
    "nervous_scholar": create_civilian_tree,
    "charismatic_rebel": create_guard_tree,
    "enigmatic_oracle": create_civilian_tree,
}


def get_tree_for_archetype(archetype: str) -> BTNode:
    """Get a behavior tree instance for the given archetype."""
    factory = ARCHETYPE_TREES.get(archetype.lower(), create_civilian_tree)
    return factory()


def evaluate_npc_behavior(
    npc_name: str,
    archetype: str,
    player_name: str,
    player_reputation: float = 0.5,
    npc_reputation: float = 0.0,
    faction_reputation: float = 0.0,
    in_combat: bool = False,
    threat_level: float = 0.0,
    has_quest: bool = False,
    quest_name: str = "",
    health: float = 1.0,
    memory_summary: str = "",
    recent_memory_flags: list[str] | None = None,
    **kwargs,
) -> BTContext:
    """
    Evaluate an NPC's behavior tree and return the resulting context.
    
    Returns:
        BTContext with action and dialogue_intent populated
    """
    # Build context
    context = BTContext(
        npc_name=npc_name,
        archetype=archetype,
        player_name=player_name,
        player_reputation=player_reputation,
        npc_reputation=npc_reputation,
        faction_reputation=faction_reputation,
        disposition=player_reputation,  # Use reputation as disposition
        in_combat=in_combat,
        threat_level=threat_level,
        has_quest=has_quest,
        quest_name=quest_name,
        health=health,
        memory_summary=memory_summary,
        recent_memory_flags=recent_memory_flags or [],
        player_nearby=True,
        **{k: v for k, v in kwargs.items() if hasattr(BTContext, k)},
    )
    
    # Get and run tree
    tree = get_tree_for_archetype(archetype)
    tree.execute(context)
    
    return context
