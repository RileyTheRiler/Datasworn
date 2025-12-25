"""
Character Progression System

Narrative-driven character advancement replacing traditional XP.
Integrates with Starforged's legacy track system and milestones.

Features:
- Narrative Milestone achievements
- Diegetic advancement triggers
- Legacy track integration
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class ProgressionType(Enum):
    """Types of character progression."""
    NARRATIVE_MILESTONE = "narrative_milestone"
    LEGACY_QUESTS = "legacy_quests"
    LEGACY_BONDS = "legacy_bonds"
    LEGACY_DISCOVERIES = "legacy_discoveries"


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
class AdvancementMoment:
    """A moment where the character can advance (get upgrades)."""
    trigger_type: str
    description: str
    timestamp: str
    scene_number: int = 0
    available: bool = True  # Has this advancement been spent/used?

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_type": self.trigger_type,
            "description": self.description,
            "timestamp": self.timestamp,
            "scene_number": self.scene_number,
            "available": self.available,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdvancementMoment":
        return cls(
            trigger_type=data["trigger_type"],
            description=data["description"],
            timestamp=data["timestamp"],
            scene_number=data.get("scene_number", 0),
            available=data.get("available", True),
        )


@dataclass
class Milestone:
    """An achievement milestone."""
    milestone_type: MilestoneType
    name: str
    description: str
    earned_at: str = ""
    scene_number: int = 0
    grants_advancement: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "milestone_type": self.milestone_type.value,
            "name": self.name,
            "description": self.description,
            "earned_at": self.earned_at,
            "scene_number": self.scene_number,
            "grants_advancement": self.grants_advancement,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Milestone":
        return cls(
            milestone_type=MilestoneType(data["milestone_type"]),
            name=data["name"],
            description=data.get("description", ""),
            earned_at=data.get("earned_at", ""),
            scene_number=data.get("scene_number", 0),
            grants_advancement=data.get("grants_advancement", False),
        )


# Milestone definitions - Now purely narrative triggers
MILESTONE_DEFINITIONS: Dict[MilestoneType, Dict[str, Any]] = {
    MilestoneType.FIRST_VOW: {
        "name": "Oath Keeper",
        "description": "Swore your first iron vow",
        "grants_advancement": False,
    },
    MilestoneType.VOW_FULFILLED: {
        "name": "Promise Kept",
        "description": "Fulfilled an iron vow",
        "grants_advancement": True,
    },
    MilestoneType.EPIC_VOW: {
        "name": "Legend in the Making",
        "description": "Completed an epic vow",
        "grants_advancement": True,
    },
    MilestoneType.FIRST_BOND: {
        "name": "Connected",
        "description": "Forged your first bond",
        "grants_advancement": False,
    },
    MilestoneType.STRONG_BONDS: {
        "name": "Trusted Ally",
        "description": "Forged 5 bonds",
        "grants_advancement": True,
    },
    MilestoneType.DISCOVERY: {
        "name": "Pathfinder",
        "description": "Made a significant discovery",
        "grants_advancement": False, 
    },
    MilestoneType.SURVIVED_DEATH: {
        "name": "Death Defier",
        "description": "Faced death and survived",
        "grants_advancement": True,
    },
    MilestoneType.COMBAT_MASTER: {
        "name": "Battle-Tested",
        "description": "Won 10 combats",
        "grants_advancement": True,
    },
    MilestoneType.EXPLORER: {
        "name": "Star Wanderer",
        "description": "Visited 10 locations",
        "grants_advancement": True,
    },
    MilestoneType.DIPLOMAT: {
        "name": "Silver Tongue",
        "description": "Successfully negotiated 5 conflicts",
        "grants_advancement": True,
    },
}


class CharacterProgressionEngine:
    """
    Engine for narrative-driven character advancement.
    
    Replaces XP with 'Advancement Moments' triggered by story milestones.
    """

    def __init__(self):
        self._milestones: Dict[MilestoneType, Milestone] = {}
        self._advancements: List[AdvancementMoment] = []
        self._current_scene: int = 0

        # Tracking for milestone triggers
        self._vows_fulfilled: int = 0
        self._bonds_forged: int = 0
        self._combats_won: int = 0
        self._locations_visited: int = 0
        self._negotiations_won: int = 0

    @property
    def available_advancements(self) -> int:
        """Number of unused advancement moments."""
        return sum(1 for a in self._advancements if a.available)

    def set_scene(self, scene_number: int):
        """Set current scene for tracking."""
        self._current_scene = scene_number

    def award_advancement(self, source: str) -> AdvancementMoment:
        """Grant a narrative advancement moment."""
        moment = AdvancementMoment(
            trigger_type="narrative",
            description=source,
            timestamp=datetime.now().isoformat(),
            scene_number=self._current_scene,
            available=True
        )
        self._advancements.append(moment)
        return moment

    def spend_advancement(self) -> bool:
        """Mark an advancement as used (e.g. purchasing an asset)."""
        available_moments = [a for a in self._advancements if a.available]
        if not available_moments:
            return False
        
        # Mark the oldest one as used
        available_moments[0].available = False
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
            grants_advancement=definition.get("grants_advancement", False),
        )

        self._milestones[milestone_type] = milestone

        # Award Advancement if milestone grants one
        if milestone.grants_advancement:
            self.award_advancement(f"Milestone: {milestone.name}")

        return milestone

    def record_vow_fulfilled(self, is_epic: bool = False) -> List[Milestone]:
        """Record a vow fulfillment and check milestones."""
        self._vows_fulfilled += 1
        milestones = []

        # Check first vow
        if self._vows_fulfilled == 1:
            m = self.check_milestone(MilestoneType.FIRST_VOW) # Fix: Was VOW_FULFILLED, logic was slightly off in old code too
            if m:
                milestones.append(m)
        
        # Standard vow fulfillment always grants a shot at advancement in this system? 
        # Or should we just stick to specific milestones? 
        # Let's say every 3 vows grants an advancement if not an epic vow?
        # For Option B, let's keep it tied to specific 'Major' milestones for now to avoid inflation.
        m = self.check_milestone(MilestoneType.VOW_FULFILLED) # Achievement for first time
        if m:
            milestones.append(m)

        # Check epic vow
        if is_epic:
            m = self.check_milestone(MilestoneType.EPIC_VOW)
            if m:
                milestones.append(m)
                
        # Fallback: In "Option B", completing vows is the MAIN way to grow.
        # So we should probably grant an advancement for *every* Epic vow, or every few normal vows.
        # Logic: If no specific milestone awarded advancement, grant a generic "Vow Completed" advancement?
        # Let's keep it simple: Completing a Vow allows you to mark progress. 
        # We will award a generic advancement for every 2 fulfilled vows for pacing.
        if self._vows_fulfilled % 2 == 0:
             self.award_advancement("Vows Fulfilled (2)")

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
    
    def check_narrative_advancement(self, narrative_summary: str) -> Optional[AdvancementMoment]:
        """
        AI-driven check: Does this narrative summary imply a major moment of growth?
        Used by the Director/Enhancement engine to award arbitrary milestones.
        """
        # Simple heuristic keywords for now, could be LLM powered later
        keywords = ["changed forever", "learned a lesson", "new understanding", "training complete"]
        if any(k in narrative_summary.lower() for k in keywords):
             return self.award_advancement("Narrative Breakthrough")
        return None

    def get_progression_summary(self) -> str:
        """Get a summary of character progression."""
        lines = [
            f"**Advancements Available**: {self.available_advancements}",
            f"**Milestones**: {len(self._milestones)} earned",
        ]

        if self._milestones:
            recent = list(self._milestones.values())[-3:]
            for m in recent:
                lines.append(f"  • {m.name}")

        return "\n".join(lines)

    def get_narrator_context(self) -> str:
        """Generate progression context for narrator."""
        if self.available_advancements > 0:
            return f"[SYSTEM: Character has {self.available_advancements} pending advancements. Offer an opportunity to learn a new Asset or upgrade if appropriate for the story.]"
        
        if not self._milestones:
            return ""

        recent = list(self._milestones.values())[-2:]
        achievements = ", ".join(m.name for m in recent)
        return f"[ACHIEVEMENTS: {achievements}]"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize engine state."""
        return {
            "milestones": {k.value: v.to_dict() for k, v in self._milestones.items()},
            "advancements": [a.to_dict() for a in self._advancements],
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
        engine._milestones = {
            MilestoneType(k): Milestone.from_dict(v)
            for k, v in data.get("milestones", {}).items()
        }
        engine._advancements = [
            AdvancementMoment.from_dict(a) for a in data.get("advancements", [])
        ]
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
    print("NARRATIVE PROGRESSION TEST")
    print("=" * 60)

    engine = CharacterProgressionEngine()

    # Record specific milestones
    print("\n--- Recording Milestones ---")
    engine.record_vow_fulfilled(is_epic=True) # Should grant advancement
    engine.record_vow_fulfilled() # Standard
    engine.record_vow_fulfilled() # Standard (Total 3, should trigger every-2 bonus)

    print(engine.get_progression_summary())
    
    print("\n--- Context Injection ---")
    print(engine.get_narrator_context())

    print("\n--- Spending Advancement ---")
    if engine.spend_advancement():
        print("Spent one advancement.")
    else:
        print("No advancements to spend.")
    print(engine.get_progression_summary())

    print("\n--- Narrative Advancement Check ---")
    m = engine.check_narrative_advancement("The character learned a profound lesson about trust.")
    if m:
        print(f"Narrative advancement awarded: {m.description}")
    print(engine.get_progression_summary())

    print("\n--- Serialization Test ---")
    data = engine.to_dict()
    print(f"Serialized data: {data}")
    new_engine = CharacterProgressionEngine.from_dict(data)
    print(f"Deserialized engine summary: {new_engine.get_progression_summary()}")
    assert new_engine.available_advancements == engine.available_advancements
    assert new_engine._vows_fulfilled == engine._vows_fulfilled
    print("Serialization/Deserialization successful!")
