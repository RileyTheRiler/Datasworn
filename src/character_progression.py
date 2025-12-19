"""
Character Progression System

Advanced character advancement beyond basic XP tracking.
Integrates with Starforged's legacy track system.

Features:
- Experience tracking
- Milestone achievements
- Ability unlocks
- Legacy track integration
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class ProgressionType(Enum):
    """Types of character progression."""
    EXPERIENCE = "experience"
    LEGACY_QUESTS = "legacy_quests"
    LEGACY_BONDS = "legacy_bonds"
    LEGACY_DISCOVERIES = "legacy_discoveries"
    ASSET_UPGRADE = "asset_upgrade"
    STAT_INCREASE = "stat_increase"


class MilestoneType(Enum):
    """Types of achievements/milestones."""
    FIRST_VOW = "first_vow"
    VOW_FULFILLED = "vow_fulfilled"
    EPIC_VOW = "epic_vow"
    FIRST_BOND = "first_bond"
    STRONG_BONDS = "strong_bonds"
    DISCOVERY = "discovery"
    SURVIVED_DEATH = "survived_death"
    COMBAT_MASTER = "combat_master"
    EXPLORER = "explorer"
    DIPLOMAT = "diplomat"


@dataclass
class Milestone:
    """An achievement milestone."""
    milestone_type: MilestoneType
    name: str
    description: str
    earned_at: str = ""
    scene_number: int = 0
    rewards: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "milestone_type": self.milestone_type.value,
            "name": self.name,
            "description": self.description,
            "earned_at": self.earned_at,
            "scene_number": self.scene_number,
            "rewards": self.rewards,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Milestone":
        return cls(
            milestone_type=MilestoneType(data["milestone_type"]),
            name=data["name"],
            description=data.get("description", ""),
            earned_at=data.get("earned_at", ""),
            scene_number=data.get("scene_number", 0),
            rewards=data.get("rewards", []),
        )


@dataclass
class ProgressionRecord:
    """Record of XP gain."""
    amount: int
    source: str
    timestamp: str
    scene_number: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": self.amount,
            "source": self.source,
            "timestamp": self.timestamp,
            "scene_number": self.scene_number,
        }


# Milestone definitions
MILESTONE_DEFINITIONS: Dict[MilestoneType, Dict[str, Any]] = {
    MilestoneType.FIRST_VOW: {
        "name": "Oath Keeper",
        "description": "Swore your first iron vow",
        "rewards": ["Unlocked vow tracking"],
    },
    MilestoneType.VOW_FULFILLED: {
        "name": "Promise Kept",
        "description": "Fulfilled an iron vow",
        "rewards": ["+2 XP"],
    },
    MilestoneType.EPIC_VOW: {
        "name": "Legend in the Making",
        "description": "Completed an epic vow",
        "rewards": ["+5 XP", "Legacy milestone"],
    },
    MilestoneType.FIRST_BOND: {
        "name": "Connected",
        "description": "Forged your first bond",
        "rewards": ["Bond abilities available"],
    },
    MilestoneType.STRONG_BONDS: {
        "name": "Trusted Ally",
        "description": "Forged 5 bonds",
        "rewards": ["+2 XP", "Social leverage"],
    },
    MilestoneType.DISCOVERY: {
        "name": "Pathfinder",
        "description": "Made a significant discovery",
        "rewards": ["+1 XP"],
    },
    MilestoneType.SURVIVED_DEATH: {
        "name": "Death Defier",
        "description": "Faced death and survived",
        "rewards": ["Story resilience"],
    },
    MilestoneType.COMBAT_MASTER: {
        "name": "Battle-Tested",
        "description": "Won 10 combats",
        "rewards": ["+2 XP", "Combat insight"],
    },
    MilestoneType.EXPLORER: {
        "name": "Star Wanderer",
        "description": "Visited 10 locations",
        "rewards": ["+2 XP", "Navigation insight"],
    },
    MilestoneType.DIPLOMAT: {
        "name": "Silver Tongue",
        "description": "Successfully negotiated 5 conflicts",
        "rewards": ["+2 XP", "Social insight"],
    },
}


class CharacterProgressionEngine:
    """
    Engine for tracking character advancement.

    Features:
    - XP tracking and spending
    - Milestone achievements
    - Legacy track integration
    - Progression narratives
    """

    def __init__(self):
        self._total_xp: int = 0
        self._spent_xp: int = 0
        self._milestones: Dict[MilestoneType, Milestone] = {}
        self._xp_history: List[ProgressionRecord] = []
        self._current_scene: int = 0

        # Tracking for milestone triggers
        self._vows_fulfilled: int = 0
        self._bonds_forged: int = 0
        self._combats_won: int = 0
        self._locations_visited: int = 0
        self._negotiations_won: int = 0

    @property
    def available_xp(self) -> int:
        """XP available to spend."""
        return self._total_xp - self._spent_xp

    def set_scene(self, scene_number: int):
        """Set current scene for tracking."""
        self._current_scene = scene_number

    def award_xp(self, amount: int, source: str) -> ProgressionRecord:
        """Award XP to the character."""
        record = ProgressionRecord(
            amount=amount,
            source=source,
            timestamp=datetime.now().isoformat(),
            scene_number=self._current_scene,
        )

        self._total_xp += amount
        self._xp_history.append(record)
        return record

    def spend_xp(self, amount: int, purpose: str) -> bool:
        """
        Spend XP on an upgrade.

        Returns True if successful, False if insufficient XP.
        """
        if amount > self.available_xp:
            return False

        self._spent_xp += amount
        self._xp_history.append(ProgressionRecord(
            amount=-amount,
            source=f"Spent: {purpose}",
            timestamp=datetime.now().isoformat(),
            scene_number=self._current_scene,
        ))
        return True

    def check_milestone(self, milestone_type: MilestoneType) -> Optional[Milestone]:
        """
        Check if a milestone should be awarded.

        Returns the Milestone if earned, None otherwise.
        """
        if milestone_type in self._milestones:
            return None  # Already earned

        definition = MILESTONE_DEFINITIONS.get(milestone_type)
        if not definition:
            return None

        milestone = Milestone(
            milestone_type=milestone_type,
            name=definition["name"],
            description=definition["description"],
            earned_at=datetime.now().isoformat(),
            scene_number=self._current_scene,
            rewards=definition.get("rewards", []),
        )

        self._milestones[milestone_type] = milestone

        # Award XP rewards
        for reward in milestone.rewards:
            if reward.startswith("+") and "XP" in reward:
                try:
                    xp = int(reward.split("+")[1].split()[0])
                    self.award_xp(xp, f"Milestone: {milestone.name}")
                except (ValueError, IndexError):
                    pass

        return milestone

    def record_vow_fulfilled(self, is_epic: bool = False) -> List[Milestone]:
        """Record a vow fulfillment and check milestones."""
        self._vows_fulfilled += 1
        milestones = []

        # Check first vow
        if self._vows_fulfilled == 1:
            m = self.check_milestone(MilestoneType.VOW_FULFILLED)
            if m:
                milestones.append(m)

        # Check epic vow
        if is_epic:
            m = self.check_milestone(MilestoneType.EPIC_VOW)
            if m:
                milestones.append(m)

        return milestones

    def record_bond_forged(self) -> Optional[Milestone]:
        """Record a bond being forged."""
        self._bonds_forged += 1

        if self._bonds_forged == 1:
            return self.check_milestone(MilestoneType.FIRST_BOND)
        elif self._bonds_forged >= 5:
            return self.check_milestone(MilestoneType.STRONG_BONDS)

        return None

    def record_combat_won(self) -> Optional[Milestone]:
        """Record a combat victory."""
        self._combats_won += 1

        if self._combats_won >= 10:
            return self.check_milestone(MilestoneType.COMBAT_MASTER)

        return None

    def record_location_visited(self) -> Optional[Milestone]:
        """Record a new location visit."""
        self._locations_visited += 1

        if self._locations_visited >= 10:
            return self.check_milestone(MilestoneType.EXPLORER)

        return None

    def record_negotiation_won(self) -> Optional[Milestone]:
        """Record a successful negotiation."""
        self._negotiations_won += 1

        if self._negotiations_won >= 5:
            return self.check_milestone(MilestoneType.DIPLOMAT)

        return None

    def record_discovery(self) -> Optional[Milestone]:
        """Record a significant discovery."""
        return self.check_milestone(MilestoneType.DISCOVERY)

    def record_survived_death(self) -> Optional[Milestone]:
        """Record surviving a death situation."""
        return self.check_milestone(MilestoneType.SURVIVED_DEATH)

    def get_progression_summary(self) -> str:
        """Get a summary of character progression."""
        lines = [
            f"**Experience**: {self._total_xp} total, {self.available_xp} available",
            f"**Milestones**: {len(self._milestones)} earned",
        ]

        if self._milestones:
            recent = list(self._milestones.values())[-3:]
            for m in recent:
                lines.append(f"  • {m.name}")

        return "\n".join(lines)

    def get_narrator_context(self) -> str:
        """Generate progression context for narrator."""
        if not self._milestones:
            return ""

        recent = list(self._milestones.values())[-2:]
        achievements = ", ".join(m.name for m in recent)

        return f"[ACHIEVEMENTS: {achievements}]"

    def get_upgrade_options(self) -> List[Dict[str, Any]]:
        """Get available upgrade options for current XP."""
        options = []

        if self.available_xp >= 3:
            options.append({
                "type": "asset_ability",
                "cost": 3,
                "description": "Unlock new asset ability",
            })

        if self.available_xp >= 2:
            options.append({
                "type": "new_asset",
                "cost": 2,
                "description": "Acquire new asset",
            })

        return options

    def to_dict(self) -> Dict[str, Any]:
        """Serialize engine state."""
        return {
            "total_xp": self._total_xp,
            "spent_xp": self._spent_xp,
            "milestones": {k.value: v.to_dict() for k, v in self._milestones.items()},
            "xp_history": [r.to_dict() for r in self._xp_history[-50:]],
            "vows_fulfilled": self._vows_fulfilled,
            "bonds_forged": self._bonds_forged,
            "combats_won": self._combats_won,
            "locations_visited": self._locations_visited,
            "negotiations_won": self._negotiations_won,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterProgressionEngine":
        """Deserialize engine state."""
        engine = cls()
        engine._total_xp = data.get("total_xp", 0)
        engine._spent_xp = data.get("spent_xp", 0)
        engine._milestones = {
            MilestoneType(k): Milestone.from_dict(v)
            for k, v in data.get("milestones", {}).items()
        }
        engine._vows_fulfilled = data.get("vows_fulfilled", 0)
        engine._bonds_forged = data.get("bonds_forged", 0)
        engine._combats_won = data.get("combats_won", 0)
        engine._locations_visited = data.get("locations_visited", 0)
        engine._negotiations_won = data.get("negotiations_won", 0)
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CHARACTER PROGRESSION TEST")
    print("=" * 60)

    engine = CharacterProgressionEngine()

    # Award some XP
    print("\n--- XP Awards ---")
    engine.award_xp(2, "Completed vow")
    engine.award_xp(1, "Discovery")
    print(f"Total XP: {engine._total_xp}, Available: {engine.available_xp}")

    # Record achievements
    print("\n--- Recording Milestones ---")

    # First vow
    milestones = engine.record_vow_fulfilled()
    for m in milestones:
        print(f"🏆 Earned: {m.name} - {m.description}")

    # Bonds
    for i in range(5):
        m = engine.record_bond_forged()
        if m:
            print(f"🏆 Earned: {m.name} - {m.description}")

    # Combats
    for i in range(10):
        m = engine.record_combat_won()
        if m:
            print(f"🏆 Earned: {m.name} - {m.description}")

    # Summary
    print("\n--- Progression Summary ---")
    print(engine.get_progression_summary())

    # Upgrade options
    print("\n--- Available Upgrades ---")
    for opt in engine.get_upgrade_options():
        print(f"- {opt['description']} ({opt['cost']} XP)")
