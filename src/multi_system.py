"""
Multi-System TTRPG Support

Abstraction layer for supporting multiple TTRPG systems beyond Starforged.
Provides interfaces for different game systems while maintaining
consistent narrative engine capabilities.

This is a foundation for future expansion.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Protocol
from enum import Enum
from src.psych_profile import PsychologicalProfile, PsychologicalEngine


class DiceSystem(Enum):
    """Common TTRPG dice systems."""
    D20 = "d20"                    # D&D, Pathfinder
    D100 = "d100"                  # Call of Cthulhu
    POOL = "pool"                  # World of Darkness
    PBTA = "pbta"                  # Powered by the Apocalypse
    IRONSWORN = "ironsworn"        # Ironsworn, Starforged
    FATE = "fate"                  # Fate system
    YEAR_ZERO = "year_zero"        # Alien RPG, Mutant


class SystemCapability(Enum):
    """Capabilities a system might have."""
    ORACLES = "oracles"
    PROGRESS_TRACKS = "progress_tracks"
    MOMENTUM = "momentum"
    CONDITIONS = "conditions"
    BONDS = "bonds"
    ASSETS = "assets"
    LEGACY_TRACKS = "legacy_tracks"
    SANITY = "sanity"
    INVENTORY = "inventory"


@dataclass
class RollRequest:
    """A generic roll request."""
    roll_type: str  # action, progress, oracle, skill, etc.
    stat: Optional[str] = None
    modifier: int = 0
    adds: List[str] = field(default_factory=list)
    context: str = ""
    psych_profile: Optional["PsychologicalProfile"] = None


@dataclass
class RollResult:
    """A generic roll result."""
    success_level: str  # strong_hit, weak_hit, miss, success, failure, etc.
    roll_values: List[int] = field(default_factory=list)
    total: int = 0
    is_match: bool = False
    outcome_text: str = ""
    mechanical_effects: List[str] = field(default_factory=list)


class GameSystemAdapter(ABC):
    """Abstract base class for TTRPG system adapters."""

    @property
    @abstractmethod
    def system_name(self) -> str:
        """Name of the game system."""
        pass

    @property
    @abstractmethod
    def dice_system(self) -> DiceSystem:
        """Dice system used."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[SystemCapability]:
        """List of system capabilities."""
        pass

    @abstractmethod
    def roll(self, request: RollRequest) -> RollResult:
        """Perform a roll for this system."""
        pass

    @abstractmethod
    def get_move(self, move_name: str) -> Optional[Dict[str, Any]]:
        """Get a move/action by name."""
        pass

    @abstractmethod
    def get_oracle(self, oracle_path: str) -> Optional[Any]:
        """Get an oracle table."""
        pass

    @abstractmethod
    def roll_oracle(self, oracle_path: str) -> Optional[str]:
        """Roll on an oracle table."""
        pass

    @abstractmethod
    def create_character_template(self) -> Dict[str, Any]:
        """Get a blank character template."""
        pass


class StarforgedAdapter(GameSystemAdapter):
    """Adapter for Ironsworn: Starforged."""

    def __init__(self, datasworn_data=None):
        self._data = datasworn_data
        self._load_data()

    def _load_data(self):
        """Load Starforged data."""
        if self._data is None:
            try:
                from src.datasworn import load_starforged_data
                self._data = load_starforged_data()
            except Exception:
                self._data = None

    @property
    def system_name(self) -> str:
        return "Ironsworn: Starforged"

    @property
    def dice_system(self) -> DiceSystem:
        return DiceSystem.IRONSWORN

    @property
    def capabilities(self) -> List[SystemCapability]:
        return [
            SystemCapability.ORACLES,
            SystemCapability.PROGRESS_TRACKS,
            SystemCapability.MOMENTUM,
            SystemCapability.CONDITIONS,
            SystemCapability.BONDS,
            SystemCapability.ASSETS,
            SystemCapability.LEGACY_TRACKS,
        ]

    def roll(self, request: RollRequest) -> RollResult:
        """Perform a Starforged roll."""
        import random

        action_die = random.randint(1, 6)
        challenge_dice = [random.randint(1, 10), random.randint(1, 10)]

        # Add stat and modifiers
        stat_value = request.modifier  # Would come from character
        
        # Apply psychological modifiers
        psych_modifier = 0
        if request.psych_profile:
            engine = PsychologicalEngine()
            psych_modifier = engine.get_move_modifier(request.psych_profile, request.stat or "")
        
        total = action_die + stat_value + psych_modifier

        # Determine outcome
        hits = sum(1 for c in challenge_dice if total > c)
        is_match = challenge_dice[0] == challenge_dice[1]

        if hits == 2:
            success_level = "strong_hit"
            outcome_text = "Strong Hit!"
        elif hits == 1:
            success_level = "weak_hit"
            outcome_text = "Weak Hit"
        else:
            success_level = "miss"
            outcome_text = "Miss"

        if is_match:
            outcome_text += " (MATCH!)"

        return RollResult(
            success_level=success_level,
            roll_values=[action_die] + challenge_dice,
            total=total,
            is_match=is_match,
            outcome_text=outcome_text,
        )

    def get_move(self, move_name: str) -> Optional[Dict[str, Any]]:
        """Get a Starforged move."""
        if not self._data:
            return None
        move = self._data.get_move(move_name)
        if move:
            return {
                "name": move.name,
                "trigger": move.trigger_text,
                "strong_hit": move.strong_hit,
                "weak_hit": move.weak_hit,
                "miss": move.miss,
            }
        return None

    def get_oracle(self, oracle_path: str) -> Optional[Any]:
        """Get a Starforged oracle."""
        if not self._data:
            return None
        return self._data.get_oracle(oracle_path)

    def roll_oracle(self, oracle_path: str) -> Optional[str]:
        """Roll on a Starforged oracle."""
        if not self._data:
            return None
        return self._data.roll_oracle(oracle_path)

    def create_character_template(self) -> Dict[str, Any]:
        """Create a Starforged character template."""
        return {
            "name": "",
            "stats": {
                "edge": 1,
                "heart": 1,
                "iron": 1,
                "shadow": 1,
                "wits": 1,
            },
            "condition": {
                "health": 5,
                "spirit": 5,
                "supply": 5,
            },
            "momentum": {"value": 2, "max": 10, "reset": 2},
            "assets": [],
            "vows": [],
            "legacy_tracks": {
                "quests": 0,
                "bonds": 0,
                "discoveries": 0,
            },
        }


class GenericPbtAAdapter(GameSystemAdapter):
    """Generic adapter for Powered by the Apocalypse games."""

    def __init__(self, system_name: str = "PbtA Game"):
        self._name = system_name

    @property
    def system_name(self) -> str:
        return self._name

    @property
    def dice_system(self) -> DiceSystem:
        return DiceSystem.PBTA

    @property
    def capabilities(self) -> List[SystemCapability]:
        return [
            SystemCapability.CONDITIONS,
            SystemCapability.BONDS,
        ]

    def roll(self, request: RollRequest) -> RollResult:
        """Perform a 2d6+stat roll."""
        import random

        dice = [random.randint(1, 6), random.randint(1, 6)]
        total = sum(dice) + request.modifier

        if total >= 10:
            success_level = "strong_hit"
            outcome_text = "10+: Strong Hit!"
        elif total >= 7:
            success_level = "weak_hit"
            outcome_text = "7-9: Weak Hit"
        else:
            success_level = "miss"
            outcome_text = "6-: Miss"

        return RollResult(
            success_level=success_level,
            roll_values=dice,
            total=total,
            outcome_text=outcome_text,
        )

    def get_move(self, move_name: str) -> Optional[Dict[str, Any]]:
        return None  # Would be system-specific

    def get_oracle(self, oracle_path: str) -> Optional[Any]:
        return None

    def roll_oracle(self, oracle_path: str) -> Optional[str]:
        return None

    def create_character_template(self) -> Dict[str, Any]:
        return {
            "name": "",
            "playbook": "",
            "stats": {},
            "moves": [],
            "gear": [],
        }


class SystemRegistry:
    """Registry for available game system adapters."""

    _adapters: Dict[str, GameSystemAdapter] = {}

    @classmethod
    def register(cls, adapter: GameSystemAdapter):
        """Register a system adapter."""
        cls._adapters[adapter.system_name.lower()] = adapter

    @classmethod
    def get(cls, system_name: str) -> Optional[GameSystemAdapter]:
        """Get a registered adapter."""
        return cls._adapters.get(system_name.lower())

    @classmethod
    def list_systems(cls) -> List[str]:
        """List registered systems."""
        return list(cls._adapters.keys())

    @classmethod
    def get_default(cls) -> Optional[GameSystemAdapter]:
        """Get the default (Starforged) adapter."""
        return cls.get("ironsworn: starforged")


# Register default adapters
def initialize_systems():
    """Initialize and register default system adapters."""
    SystemRegistry.register(StarforgedAdapter())
    SystemRegistry.register(GenericPbtAAdapter("Generic PbtA"))


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MULTI-SYSTEM SUPPORT TEST")
    print("=" * 60)

    initialize_systems()

    print("\n--- Registered Systems ---")
    for system in SystemRegistry.list_systems():
        adapter = SystemRegistry.get(system)
        print(f"• {adapter.system_name} ({adapter.dice_system.value})")
        print(f"  Capabilities: {[c.value for c in adapter.capabilities]}")

    # Test Starforged roll
    print("\n--- Starforged Roll Test ---")
    starforged = SystemRegistry.get("ironsworn: starforged")
    if starforged:
        result = starforged.roll(RollRequest(
            roll_type="action",
            stat="heart",
            modifier=2,
            context="Making a connection",
        ))
        print(f"Roll: {result.roll_values}")
        print(f"Total: {result.total}")
        print(f"Result: {result.outcome_text}")

    # Test PbtA roll
    print("\n--- PbtA Roll Test ---")
    pbta = SystemRegistry.get("generic pbta")
    if pbta:
        result = pbta.roll(RollRequest(
            roll_type="move",
            modifier=1,
        ))
        print(f"Roll: {result.roll_values}")
        print(f"Total: {result.total}")
        print(f"Result: {result.outcome_text}")

    # Character templates
    print("\n--- Character Templates ---")
    if starforged:
        template = starforged.create_character_template()
        print(f"Starforged stats: {list(template['stats'].keys())}")
