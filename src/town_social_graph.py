"""
Town Social Graph Simulation

Implements a lightweight social graph for town NPCs, covering relationships,
routines, interactions, and player-facing surfacing mechanisms. The system is
built for fast background simulation with performance safeguards.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import random


class RelationshipType(Enum):
    """Types of social relationships."""

    FRIEND = "friend"
    RIVAL = "rival"
    NEUTRAL = "neutral"


class Role(Enum):
    """Town-facing roles for NPCs."""

    SHOPKEEPER = "shopkeeper"
    GUARD = "guard"
    NOBLE = "noble"
    MERCHANT = "merchant"
    CRAFTSPERSON = "craftsperson"
    LABORER = "laborer"
    INFORMANT = "informant"


class InteractionType(Enum):
    """Interactions that mutate the social graph."""

    GOSSIP = "gossip"
    TRADE = "trade"
    CONFLICT = "conflict"


class LOD(Enum):
    """Level-of-detail for AI updates."""

    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()

    @property
    def interval_days(self) -> int:
        """How often this LOD should run full updates."""

        if self is LOD.HIGH:
            return 1
        if self is LOD.MEDIUM:
            return 2
        return 4


@dataclass
class Relationship:
    """Edge between two NPCs in the social graph."""

    target_id: str
    relationship_type: RelationshipType
    strength: float = 0.0  # -1.0 (hostile) to 1.0 (very strong)

    def adjust(self, delta: float) -> None:
        self.strength = max(-1.0, min(1.0, self.strength + delta))


@dataclass
class NPCNode:
    """A node in the town social graph."""

    npc_id: str
    name: str
    role: Role
    home: str
    shop_inventory: List[str] = field(default_factory=list)
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    routine_bias: float = 0.1  # How likely they deviate from routine
    notoriety: float = 0.0
    last_updated_day: int = 0
    lod: LOD = LOD.HIGH

    def set_relationship(self, other_id: str, relationship_type: RelationshipType, strength: float = 0.1) -> None:
        self.relationships[other_id] = Relationship(other_id, relationship_type, strength)

    def adjust_relationship(self, other_id: str, delta: float) -> None:
        if other_id not in self.relationships:
            self.relationships[other_id] = Relationship(other_id, RelationshipType.NEUTRAL, 0.0)
        self.relationships[other_id].adjust(delta)


@dataclass
class SocialOutcome:
    """Player-facing results of simulation ticks."""

    overheard_dialogue: List[str] = field(default_factory=list)
    bounties: List[str] = field(default_factory=list)
    inventory_changes: Dict[str, List[str]] = field(default_factory=dict)

    def extend(self, other: "SocialOutcome") -> None:
        self.overheard_dialogue.extend(other.overheard_dialogue)
        self.bounties.extend(other.bounties)
        for npc_id, changes in other.inventory_changes.items():
            self.inventory_changes.setdefault(npc_id, []).extend(changes)

    def clear(self) -> None:
        self.overheard_dialogue.clear()
        self.bounties.clear()
        self.inventory_changes.clear()


class TownSocialGraph:
    """Lightweight social graph for town NPCs."""

    def __init__(self):
        self.npcs: Dict[str, NPCNode] = {}
        self.day_counter = 0
        self.week_counter = 0
        self._tick_budget = 100
        self._outcomes = SocialOutcome()

    # ------------------------------------------------------------------
    # Graph management
    # ------------------------------------------------------------------
    def add_npc(self, npc_id: str, name: str, role: Role, home: str, shop_inventory: Optional[List[str]] = None,
                lod: LOD = LOD.HIGH) -> NPCNode:
        node = NPCNode(
            npc_id=npc_id,
            name=name,
            role=role,
            home=home,
            shop_inventory=shop_inventory or [],
            lod=lod,
        )
        self.npcs[npc_id] = node
        return node

    def set_relationship(self, source_id: str, target_id: str, relationship_type: RelationshipType, strength: float = 0.1) -> None:
        if source_id not in self.npcs or target_id not in self.npcs:
            return
        self.npcs[source_id].set_relationship(target_id, relationship_type, strength)
        self.npcs[target_id].set_relationship(source_id, relationship_type, strength)

    def adjust_relationship(self, source_id: str, target_id: str, delta: float) -> None:
        if source_id not in self.npcs or target_id not in self.npcs:
            return
        self.npcs[source_id].adjust_relationship(target_id, delta)
        self.npcs[target_id].adjust_relationship(source_id, delta)

    # ------------------------------------------------------------------
    # Simulation control
    # ------------------------------------------------------------------
    def set_tick_budget(self, budget: int) -> None:
        """Limit work performed per advance call."""

        self._tick_budget = max(10, budget)

    def advance_day(self) -> SocialOutcome:
        """Run daily routines with random perturbations and interactions."""

        self.day_counter += 1
        operations_remaining = self._tick_budget
        outcome = SocialOutcome()

        for npc in self._active_npcs_for_day():
            if operations_remaining <= 0:
                break
            operations_remaining -= 1
            daily_outcome = self._run_daily_routine(npc)
            outcome.extend(daily_outcome)
            npc.last_updated_day = self.day_counter

        self._outcomes.extend(outcome)
        return outcome

    def advance_week(self) -> SocialOutcome:
        """Run weekly routines; more strategic changes with budget limits."""

        self.week_counter += 1
        operations_remaining = self._tick_budget
        outcome = SocialOutcome()

        # Weekly updates only for higher LOD NPCs to save budget
        for npc in self._active_npcs_for_week():
            if operations_remaining <= 0:
                break
            operations_remaining -= 2  # weekly processing is heavier
            weekly_outcome = self._run_weekly_routine(npc)
            outcome.extend(weekly_outcome)

        self._outcomes.extend(outcome)
        return outcome

    def consume_outcomes(self) -> SocialOutcome:
        """Return and clear accumulated player-facing outcomes."""

        snapshot = SocialOutcome(
            overheard_dialogue=list(self._outcomes.overheard_dialogue),
            bounties=list(self._outcomes.bounties),
            inventory_changes={k: list(v) for k, v in self._outcomes.inventory_changes.items()},
        )
        self._outcomes.clear()
        return snapshot

    # ------------------------------------------------------------------
    # Routines and interactions
    # ------------------------------------------------------------------
    def _run_daily_routine(self, npc: NPCNode) -> SocialOutcome:
        outcome = SocialOutcome()

        # Daily schedule baseline
        if npc.role in {Role.SHOPKEEPER, Role.MERCHANT, Role.CRAFTSPERSON}:
            if random.random() < 0.2:
                change = self._perturb_inventory(npc)
                if change:
                    outcome.inventory_changes[npc.npc_id] = change
        elif npc.role is Role.GUARD:
            if random.random() < 0.15:
                bounty_text = f"Guard captain {npc.name} posted a bounty after patrol skirmishes."
                outcome.bounties.append(bounty_text)

        # Random interaction chance
        if random.random() < 0.5:
            target = self._pick_interaction_target(npc)
            if target:
                interaction_outcome = self._handle_interaction(npc, target)
                outcome.extend(interaction_outcome)

        return outcome

    def _run_weekly_routine(self, npc: NPCNode) -> SocialOutcome:
        outcome = SocialOutcome()
        # Weekly arcs: rivalries escalate, friendships deepen
        for other_id, relation in npc.relationships.items():
            if relation.relationship_type is RelationshipType.RIVAL and random.random() < 0.3:
                self.adjust_relationship(npc.npc_id, other_id, -0.1)
                dialogue = f"Heated rivalry between {npc.name} and {self.npcs[other_id].name} is now public knowledge."
                outcome.overheard_dialogue.append(dialogue)
            elif relation.relationship_type is RelationshipType.FRIEND and random.random() < 0.25:
                self.adjust_relationship(npc.npc_id, other_id, 0.1)
                dialogue = f"{npc.name} and {self.npcs[other_id].name} planned a festival together, boosting morale."
                outcome.overheard_dialogue.append(dialogue)

        # Weekly economic shifts
        if npc.role in {Role.MERCHANT, Role.SHOPKEEPER} and random.random() < 0.3:
            change = self._perturb_inventory(npc, major=True)
            if change:
                outcome.inventory_changes[npc.npc_id] = change

        # Notoriety spillover
        if npc.notoriety > 0.6:
            bounty = f"Wanted poster: {npc.name} (notoriety {npc.notoriety:.1f})"
            outcome.bounties.append(bounty)
            npc.notoriety *= 0.9  # decay to avoid runaway

        return outcome

    def _handle_interaction(self, npc: NPCNode, target: NPCNode) -> SocialOutcome:
        outcome = SocialOutcome()
        interaction = random.choices(
            population=[InteractionType.GOSSIP, InteractionType.TRADE, InteractionType.CONFLICT],
            weights=[0.4, 0.35, 0.25],
            k=1,
        )[0]

        if interaction is InteractionType.GOSSIP:
            self.adjust_relationship(npc.npc_id, target.npc_id, 0.05)
            line = f"Overheard: {npc.name} shared rumors with {target.name} about shifting alliances."
            outcome.overheard_dialogue.append(line)
        elif interaction is InteractionType.TRADE:
            self.adjust_relationship(npc.npc_id, target.npc_id, 0.02)
            if npc.role is Role.MERCHANT:
                change = self._perturb_inventory(npc)
                if change:
                    outcome.inventory_changes[npc.npc_id] = change
            if target.role is Role.MERCHANT:
                change = self._perturb_inventory(target)
                if change:
                    outcome.inventory_changes[target.npc_id] = change
        else:  # CONFLICT
            self.adjust_relationship(npc.npc_id, target.npc_id, -0.15)
            npc.notoriety = min(1.0, npc.notoriety + 0.1)
            target.notoriety = min(1.0, target.notoriety + 0.05)
            line = f"Conflict erupted between {npc.name} and {target.name} near {npc.home}."
            outcome.overheard_dialogue.append(line)
            if npc.role is Role.GUARD or target.role is Role.GUARD:
                bounty = f"Town watch seeks peacekeepers after clashes between {npc.name} and {target.name}."
                outcome.bounties.append(bounty)

        return outcome

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _active_npcs_for_day(self) -> List[NPCNode]:
        """Return NPCs due for daily updates based on LOD and budget."""

        # Higher LOD first; skip if not time for update
        candidates = []
        for npc in self.npcs.values():
            days_since_update = self.day_counter - npc.last_updated_day
            if days_since_update >= npc.lod.interval_days:
                candidates.append(npc)
        candidates.sort(key=lambda n: n.lod.value)  # HIGH first
        return candidates

    def _active_npcs_for_week(self) -> List[NPCNode]:
        return [n for n in self.npcs.values() if n.lod is not LOD.LOW]

    def _pick_interaction_target(self, npc: NPCNode) -> Optional[NPCNode]:
        others = [n for n in self.npcs.values() if n.npc_id != npc.npc_id]
        if not others:
            return None
        # Prefer interacting with known relationships to reduce randomness
        weighted: List[Tuple[NPCNode, float]] = []
        for other in others:
            relation = npc.relationships.get(other.npc_id)
            weight = 1.0 + (relation.strength if relation else 0.0)
            weight += 0.2 if relation and relation.relationship_type is RelationshipType.FRIEND else 0.0
            weight += -0.2 if relation and relation.relationship_type is RelationshipType.RIVAL else 0.0
            weighted.append((other, max(0.1, weight)))

        total = sum(w for _, w in weighted)
        choice = random.uniform(0, total)
        running = 0.0
        for other, weight in weighted:
            running += weight
            if running >= choice:
                return other
        return weighted[-1][0]

    def _perturb_inventory(self, npc: NPCNode, major: bool = False) -> List[str]:
        if not npc.shop_inventory:
            return []
        change = []
        sample_size = 2 if major else 1
        for item in random.sample(npc.shop_inventory, min(sample_size, len(npc.shop_inventory))):
            if random.random() < 0.5:
                npc.shop_inventory.remove(item)
                change.append(f"Removed {item}")
            else:
                upgraded = f"Premium {item}"
                npc.shop_inventory.append(upgraded)
                change.append(f"Added {upgraded}")
        return change


__all__ = [
    "InteractionType",
    "LOD",
    "NPCNode",
    "Relationship",
    "RelationshipType",
    "Role",
    "SocialOutcome",
    "TownSocialGraph",
]
