"""
Combat Flow System

Tracks initiative, combat rounds, and enemy behavior for
more structured and tactical combat encounters.

Designed to work with Starforged's narrative combat while
adding tactical depth.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import random

from src.telemetry import telemetry


class CombatPhase(Enum):
    """Phases of combat."""
    INACTIVE = "inactive"
    INITIATIVE = "initiative"
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    RESOLUTION = "resolution"


class CombatantType(Enum):
    """Types of combatants."""
    PLAYER = "player"
    ALLY = "ally"
    ENEMY = "enemy"
    NEUTRAL = "neutral"


class ThreatLevel(Enum):
    """Enemy threat levels (Starforged-style)."""
    TROUBLESOME = "troublesome"  # Minor threat, easily handled
    DANGEROUS = "dangerous"       # Moderate threat
    FORMIDABLE = "formidable"    # Serious threat
    EXTREME = "extreme"          # Major threat
    EPIC = "epic"               # Boss-level threat


@dataclass
class Combatant:
    """A participant in combat."""
    name: str
    combatant_type: CombatantType
    threat_level: ThreatLevel = ThreatLevel.DANGEROUS
    initiative: int = 0
    health: int = 5  # Progress boxes for enemies
    is_active: bool = True
    status_effects: List[str] = field(default_factory=list)
    behavior: str = "aggressive"  # aggressive, defensive, cunning, erratic
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "combatant_type": self.combatant_type.value,
            "threat_level": self.threat_level.value,
            "initiative": self.initiative,
            "health": self.health,
            "is_active": self.is_active,
            "status_effects": self.status_effects,
            "behavior": self.behavior,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Combatant":
        return cls(
            name=data["name"],
            combatant_type=CombatantType(data.get("combatant_type", "enemy")),
            threat_level=ThreatLevel(data.get("threat_level", "dangerous")),
            initiative=data.get("initiative", 0),
            health=data.get("health", 5),
            is_active=data.get("is_active", True),
            status_effects=data.get("status_effects", []),
            behavior=data.get("behavior", "aggressive"),
            description=data.get("description", ""),
        )


@dataclass
class CombatAction:
    """An action taken during combat."""
    actor: str
    action_type: str  # attack, defend, maneuver, special
    target: Optional[str] = None
    description: str = ""
    outcome: str = ""  # strong_hit, weak_hit, miss
    damage: int = 0
    effects: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "actor": self.actor,
            "action_type": self.action_type,
            "target": self.target,
            "description": self.description,
            "outcome": self.outcome,
            "damage": self.damage,
            "effects": self.effects,
        }


# Enemy behavior patterns
BEHAVIOR_PATTERNS = {
    "aggressive": {
        "attack_weight": 0.7,
        "defend_weight": 0.1,
        "maneuver_weight": 0.2,
        "attacks": [
            "strikes directly",
            "presses the attack",
            "attempts a powerful blow",
            "attacks relentlessly",
        ],
        "defends": [
            "falls back to regroup",
            "braces for counterattack",
        ],
        "maneuvers": [
            "flanks for better position",
            "creates an opening",
        ],
    },
    "defensive": {
        "attack_weight": 0.3,
        "defend_weight": 0.5,
        "maneuver_weight": 0.2,
        "attacks": [
            "strikes carefully",
            "takes a measured shot",
        ],
        "defends": [
            "maintains defensive posture",
            "waits for an opening",
            "draws back, watching carefully",
        ],
        "maneuvers": [
            "repositions defensively",
            "seeks cover",
        ],
    },
    "cunning": {
        "attack_weight": 0.4,
        "defend_weight": 0.2,
        "maneuver_weight": 0.4,
        "attacks": [
            "strikes at a vulnerability",
            "exploits a weakness",
        ],
        "defends": [
            "feints and withdraws",
            "baits you into overextending",
        ],
        "maneuvers": [
            "attempts to outmaneuver you",
            "sets up for a devastating move",
            "tries something unexpected",
        ],
    },
    "erratic": {
        "attack_weight": 0.5,
        "defend_weight": 0.2,
        "maneuver_weight": 0.3,
        "attacks": [
            "attacks wildly",
            "lunges unpredictably",
            "strikes erratically",
        ],
        "defends": [
            "backs away chaotically",
            "freezes momentarily",
        ],
        "maneuvers": [
            "moves unpredictably",
            "does something unexpected",
        ],
    },
}


class CombatFlowEngine:
    """
    Engine for managing combat flow and enemy AI.

    Features:
    - Initiative tracking
    - Enemy behavior AI
    - Combat phase management
    - Progress track integration
    - Narrative combat descriptions
    """

    def __init__(self):
        self._phase = CombatPhase.INACTIVE
        self._combatants: Dict[str, Combatant] = {}
        self._turn_order: List[str] = []
        self._current_turn_index: int = 0
        self._round_number: int = 0
        self._combat_log: List[CombatAction] = []
        self._player_control: bool = True

    def start_combat(self, enemies: List[Dict[str, Any]] = None):
        """
        Start a new combat encounter.

        Args:
            enemies: List of enemy definitions
        """
        self._phase = CombatPhase.INITIATIVE
        self._combatants = {}
        self._turn_order = []
        self._current_turn_index = 0
        self._round_number = 1
        self._combat_log = []

        # Add player
        self.add_combatant("Player", CombatantType.PLAYER)

        # Add enemies
        if enemies:
            for enemy in enemies:
                threat = ThreatLevel(enemy.get("threat_level", "dangerous"))
                self.add_combatant(
                    name=enemy.get("name", "Enemy"),
                    combatant_type=CombatantType.ENEMY,
                    threat_level=threat,
                    behavior=enemy.get("behavior", "aggressive"),
                    description=enemy.get("description", ""),
                )

    def add_combatant(
        self,
        name: str,
        combatant_type: CombatantType,
        threat_level: ThreatLevel = ThreatLevel.DANGEROUS,
        behavior: str = "aggressive",
        description: str = ""
    ):
        """Add a combatant to the encounter."""
        # Threat level determines health boxes
        health_by_threat = {
            ThreatLevel.TROUBLESOME: 3,
            ThreatLevel.DANGEROUS: 5,
            ThreatLevel.FORMIDABLE: 10,
            ThreatLevel.EXTREME: 15,
            ThreatLevel.EPIC: 20,
        }

        combatant = Combatant(
            name=name,
            combatant_type=combatant_type,
            threat_level=threat_level,
            health=health_by_threat.get(threat_level, 5),
            behavior=behavior,
            description=description,
        )

        self._combatants[name.lower()] = combatant

    def roll_initiative(self) -> List[Tuple[str, int]]:
        """Roll initiative for all combatants."""
        for combatant in self._combatants.values():
            # Basic initiative: d6 + modifiers
            roll = random.randint(1, 6)

            # Player gets a bonus
            if combatant.combatant_type == CombatantType.PLAYER:
                roll += 2
            elif combatant.combatant_type == CombatantType.ALLY:
                roll += 1

            # Threat level penalties for NPCs
            threat_mods = {
                ThreatLevel.TROUBLESOME: -1,
                ThreatLevel.DANGEROUS: 0,
                ThreatLevel.FORMIDABLE: 1,
                ThreatLevel.EXTREME: 2,
                ThreatLevel.EPIC: 3,
            }
            if combatant.combatant_type == CombatantType.ENEMY:
                roll += threat_mods.get(combatant.threat_level, 0)

            combatant.initiative = roll

        # Sort by initiative (highest first)
        sorted_combatants = sorted(
            self._combatants.values(),
            key=lambda c: c.initiative,
            reverse=True
        )

        self._turn_order = [c.name for c in sorted_combatants]
        self._phase = CombatPhase.PLAYER_TURN if self._turn_order[0] == "Player" else CombatPhase.ENEMY_TURN

        return [(c.name, c.initiative) for c in sorted_combatants]

    def get_current_turn(self) -> Optional[Combatant]:
        """Get the combatant whose turn it is."""
        if not self._turn_order or self._phase == CombatPhase.INACTIVE:
            return None

        name = self._turn_order[self._current_turn_index]
        return self._combatants.get(name.lower())

    def advance_turn(self):
        """Advance to the next combatant's turn."""
        if not self._turn_order:
            return

        # Skip defeated combatants
        attempts = 0
        while attempts < len(self._turn_order):
            self._current_turn_index = (self._current_turn_index + 1) % len(self._turn_order)

            # Check if we completed a round
            if self._current_turn_index == 0:
                self._round_number += 1

            current = self.get_current_turn()
            if current and current.is_active:
                break
            attempts += 1

        # Update phase
        current = self.get_current_turn()
        if current:
            if current.combatant_type == CombatantType.PLAYER:
                self._phase = CombatPhase.PLAYER_TURN
            elif current.combatant_type == CombatantType.ALLY:
                self._phase = CombatPhase.PLAYER_TURN  # Player controls allies
            else:
                self._phase = CombatPhase.ENEMY_TURN

    def get_enemy_action(self, enemy_name: str) -> str:
        """
        Generate an enemy action based on behavior.

        Returns a narrative description of what the enemy does.
        """
        enemy = self._combatants.get(enemy_name.lower())
        if not enemy:
            return "The enemy hesitates."

        behavior = BEHAVIOR_PATTERNS.get(enemy.behavior, BEHAVIOR_PATTERNS["aggressive"])

        # Choose action type based on weights
        roll = random.random()
        if roll < behavior["attack_weight"]:
            action_type = "attacks"
        elif roll < behavior["attack_weight"] + behavior["defend_weight"]:
            action_type = "defends"
        else:
            action_type = "maneuvers"

        # Get action description
        actions = behavior.get(action_type, ["acts"])
        description = random.choice(actions)

        return f"{enemy.name} {description}"

    def record_action(self, action: CombatAction):
        """Record a combat action."""
        self._combat_log.append(action)

        # Apply damage
        if action.damage > 0 and action.target:
            target = self._combatants.get(action.target.lower())
            if target:
                target.health = max(0, target.health - action.damage)
                if target.health <= 0:
                    target.is_active = False

    def apply_damage(self, target_name: str, damage: int) -> bool:
        """
        Apply damage to a target.

        Returns True if target is defeated.
        """
        target = self._combatants.get(target_name.lower())
        if target:
            target.health = max(0, target.health - damage)
            if target.health <= 0:
                target.is_active = False
                return True
        return False

    def end_combat(self) -> Dict[str, Any]:
        """
        End the combat and return summary.

        Returns:
            Summary of combat outcome
        """
        summary = {
            "rounds": self._round_number,
            "actions": len(self._combat_log),
            "enemies_defeated": [
                c.name for c in self._combatants.values()
                if c.combatant_type == CombatantType.ENEMY and not c.is_active
            ],
            "player_survived": self._combatants.get("player", Combatant(
                name="Player",
                combatant_type=CombatantType.PLAYER
            )).is_active,
        }

        if not summary["player_survived"]:
            telemetry.emit_wipe(
                cause="combat_defeat",
                session_id=None,
                difficulty_rating=self._estimate_difficulty_rating(),
            )

        self._phase = CombatPhase.INACTIVE
        return summary

    def get_combat_status(self) -> str:
        """Get a narrative description of combat status."""
        lines = [f"**Round {self._round_number}**"]

        active_enemies = [
            c for c in self._combatants.values()
            if c.combatant_type == CombatantType.ENEMY and c.is_active
        ]

        if not active_enemies:
            lines.append("No enemies remain!")
        else:
            for enemy in active_enemies:
                # Health description
                health_pct = enemy.health / max(1, self._get_max_health(enemy.threat_level))
                if health_pct > 0.75:
                    status = "fresh"
                elif health_pct > 0.5:
                    status = "wounded"
                elif health_pct > 0.25:
                    status = "badly hurt"
                else:
                    status = "near defeat"

                lines.append(f"- {enemy.name} ({enemy.threat_level.value}): {status}")

        current = self.get_current_turn()
        if current:
            lines.append(f"\n**{current.name}'s turn**")

        return "\n".join(lines)

    def _get_max_health(self, threat_level: ThreatLevel) -> int:
        """Get max health for a threat level."""
        return {
            ThreatLevel.TROUBLESOME: 3,
            ThreatLevel.DANGEROUS: 5,
            ThreatLevel.FORMIDABLE: 10,
            ThreatLevel.EXTREME: 15,
            ThreatLevel.EPIC: 20,
        }.get(threat_level, 5)

    def _estimate_difficulty_rating(self) -> float:
        """Estimate combat difficulty based on enemy threat levels."""

        weights = {
            ThreatLevel.TROUBLESOME: 1.0,
            ThreatLevel.DANGEROUS: 2.5,
            ThreatLevel.FORMIDABLE: 5.0,
            ThreatLevel.EXTREME: 8.0,
            ThreatLevel.EPIC: 10.0,
        }
        enemies = [
            c for c in self._combatants.values()
            if c.combatant_type == CombatantType.ENEMY
        ]
        if not enemies:
            return 0.0
        return sum(weights.get(e.threat_level, 2.0) for e in enemies) / len(enemies)

    def get_narrator_context(self) -> str:
        """Generate combat context for narrator."""
        if self._phase == CombatPhase.INACTIVE:
            return ""

        lines = [f"[COMBAT - Round {self._round_number}]"]

        for c in self._combatants.values():
            if c.is_active:
                role = "PLAYER" if c.combatant_type == CombatantType.PLAYER else c.combatant_type.value.upper()
                lines.append(f"- {c.name} ({role}): {c.health} health")

        current = self.get_current_turn()
        if current and current.combatant_type != CombatantType.PLAYER:
            # Suggest enemy action
            action = self.get_enemy_action(current.name)
            lines.append(f"\nENEMY ACTION: {action}")

        return "\n".join(lines)

    def is_in_combat(self) -> bool:
        """Check if combat is active."""
        return self._phase != CombatPhase.INACTIVE

    def to_dict(self) -> Dict[str, Any]:
        """Serialize combat state."""
        return {
            "phase": self._phase.value,
            "combatants": {k: v.to_dict() for k, v in self._combatants.items()},
            "turn_order": self._turn_order,
            "current_turn_index": self._current_turn_index,
            "round_number": self._round_number,
            "combat_log": [a.to_dict() for a in self._combat_log[-20:]],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CombatFlowEngine":
        """Deserialize combat state."""
        engine = cls()
        engine._phase = CombatPhase(data.get("phase", "inactive"))
        engine._combatants = {
            k: Combatant.from_dict(v)
            for k, v in data.get("combatants", {}).items()
        }
        engine._turn_order = data.get("turn_order", [])
        engine._current_turn_index = data.get("current_turn_index", 0)
        engine._round_number = data.get("round_number", 0)
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("COMBAT FLOW ENGINE TEST")
    print("=" * 60)

    engine = CombatFlowEngine()

    # Start combat
    engine.start_combat([
        {"name": "Pirate Captain", "threat_level": "formidable", "behavior": "aggressive"},
        {"name": "Pirate Crew", "threat_level": "troublesome", "behavior": "erratic"},
    ])

    # Roll initiative
    print("\n--- Initiative ---")
    initiative = engine.roll_initiative()
    for name, init in initiative:
        print(f"{name}: {init}")

    # Simulate combat rounds
    print("\n--- Combat Simulation ---")
    for _ in range(5):
        current = engine.get_current_turn()
        if not current:
            break

        print(f"\n{engine.get_combat_status()}")

        if current.combatant_type == CombatantType.PLAYER:
            # Player attacks
            targets = [c for c in engine._combatants.values()
                      if c.combatant_type == CombatantType.ENEMY and c.is_active]
            if targets:
                target = targets[0]
                damage = random.randint(1, 3)
                defeated = engine.apply_damage(target.name, damage)
                print(f"Player attacks {target.name} for {damage} damage!")
                if defeated:
                    print(f"{target.name} is defeated!")
        else:
            # Enemy acts
            action = engine.get_enemy_action(current.name)
            print(action)

        engine.advance_turn()

    # End combat
    print("\n--- Combat Summary ---")
    summary = engine.end_combat()
    print(f"Rounds: {summary['rounds']}")
    print(f"Defeated: {summary['enemies_defeated']}")
    print(f"Player survived: {summary['player_survived']}")
