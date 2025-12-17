"""
Combat Prediction System using Lanchester's Laws.
Provides mathematical prediction of combat fairness.

Based on Game AI Pro patterns for strategic analysis.
Lanchester's Laws model attrition warfare outcomes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import math


# ============================================================================
# Combat Force Model
# ============================================================================

class ForceType(Enum):
    """Type of combat engagement."""
    LINEAR = "linear"  # Lanchester's Linear Law (ancient/melee)
    SQUARE = "square"  # Lanchester's Square Law (modern/ranged)
    MIXED = "mixed"    # Hybrid engagement


@dataclass
class CombatUnit:
    """Represents a single unit in combat."""
    name: str
    count: int = 1
    attack_power: float = 1.0  # Damage per unit per round
    defense: float = 1.0  # Damage reduction factor
    health: float = 1.0  # 0-1 current health
    morale: float = 1.0  # 0-1 willingness to fight
    is_ranged: bool = False  # True for ranged, False for melee
    
    @property
    def effective_strength(self) -> float:
        """Calculate effective combat strength."""
        return self.count * self.attack_power * self.health * self.morale


@dataclass
class CombatForce:
    """Represents one side in a combat engagement."""
    name: str
    units: list[CombatUnit] = field(default_factory=list)
    terrain_bonus: float = 1.0  # Multiplier from terrain advantages
    surprise_bonus: float = 1.0  # Multiplier from surprise attack
    
    @property
    def total_count(self) -> int:
        """Total number of units."""
        return sum(u.count for u in self.units)
    
    @property
    def total_strength(self) -> float:
        """Total effective strength."""
        base = sum(u.effective_strength for u in self.units)
        return base * self.terrain_bonus * self.surprise_bonus
    
    @property
    def average_attack(self) -> float:
        """Average attack power across units."""
        if not self.units:
            return 0.0
        return sum(u.attack_power * u.count for u in self.units) / self.total_count
    
    @property
    def is_ranged(self) -> bool:
        """True if majority of force is ranged."""
        ranged_count = sum(u.count for u in self.units if u.is_ranged)
        return ranged_count > self.total_count / 2


# ============================================================================
# Lanchester's Laws
# ============================================================================

def lanchester_linear(force_a: CombatForce, force_b: CombatForce) -> dict:
    """
    Lanchester's Linear Law for melee/ancient combat.
    
    Attrition is proportional to the number of units.
    Advantage = (A_strength * A_count) / (B_strength * B_count)
    
    Returns:
        Dict with winner prediction and strength ratio
    """
    a_power = force_a.total_strength
    b_power = force_b.total_strength
    
    if b_power == 0:
        return {
            "winner": force_a.name,
            "ratio": float('inf'),
            "description": f"{force_a.name} has overwhelming advantage",
        }
    
    ratio = a_power / b_power
    
    if ratio > 1.5:
        winner = force_a.name
        desc = f"{force_a.name} has significant advantage"
    elif ratio < 0.67:
        winner = force_b.name
        desc = f"{force_b.name} has significant advantage"
    else:
        winner = "contested"
        desc = "Fight could go either way"
    
    return {
        "winner": winner,
        "ratio": ratio,
        "description": desc,
        "law": "linear",
    }


def lanchester_square(force_a: CombatForce, force_b: CombatForce) -> dict:
    """
    Lanchester's Square Law for ranged/modern combat.
    
    Attrition is proportional to the SQUARE of force size.
    This means numerical superiority is much more important.
    
    Fighting strength = attack_power * count^2
    
    Returns:
        Dict with winner prediction and strength ratio
    """
    a_count = force_a.total_count
    b_count = force_b.total_count
    a_attack = force_a.average_attack * force_a.terrain_bonus
    b_attack = force_b.average_attack * force_b.terrain_bonus
    
    # Square law: effective power = attack * count^2
    a_power = a_attack * (a_count ** 2)
    b_power = b_attack * (b_count ** 2)
    
    if b_power == 0:
        return {
            "winner": force_a.name,
            "ratio": float('inf'),
            "description": f"{force_a.name} will obliterate the opposition",
        }
    
    ratio = a_power / b_power
    
    # Under square law, even small numerical advantage is huge
    if ratio > 2.0:
        winner = force_a.name
        desc = f"{force_a.name} will crush the opposition (square law advantage)"
    elif ratio > 1.3:
        winner = force_a.name
        desc = f"{force_a.name} has clear advantage"
    elif ratio < 0.5:
        winner = force_b.name
        desc = f"{force_b.name} will crush the opposition (square law advantage)"
    elif ratio < 0.77:
        winner = force_b.name
        desc = f"{force_b.name} has clear advantage"
    else:
        winner = "contested"
        desc = "Fight is fairly matched"
    
    return {
        "winner": winner,
        "ratio": ratio,
        "description": desc,
        "law": "square",
    }


def predict_combat_outcome(
    force_a: CombatForce,
    force_b: CombatForce,
    force_type: ForceType = ForceType.MIXED,
) -> dict:
    """
    Predict combat outcome using appropriate Lanchester law.
    
    Args:
        force_a: First combat force (typically player)
        force_b: Second combat force (typically enemy)
        force_type: Type of combat engagement
        
    Returns:
        Dict with prediction, warning level, and narrative context
    """
    # Choose law based on combat type
    if force_type == ForceType.LINEAR:
        result = lanchester_linear(force_a, force_b)
    elif force_type == ForceType.SQUARE:
        result = lanchester_square(force_a, force_b)
    else:
        # Mixed: average of both laws, weighted by ranged proportion
        linear = lanchester_linear(force_a, force_b)
        square = lanchester_square(force_a, force_b)
        
        # Weight toward square law if both forces are ranged
        if force_a.is_ranged and force_b.is_ranged:
            weight = 0.8
        elif force_a.is_ranged or force_b.is_ranged:
            weight = 0.5
        else:
            weight = 0.2
        
        ratio = linear["ratio"] * (1 - weight) + square["ratio"] * weight
        
        if ratio > 1.5:
            winner = force_a.name
        elif ratio < 0.67:
            winner = force_b.name
        else:
            winner = "contested"
        
        result = {
            "winner": winner,
            "ratio": ratio,
            "description": f"Mixed engagement analysis",
            "law": "mixed",
        }
    
    # Add warning levels for player
    ratio = result["ratio"]
    
    if ratio < 0.3:
        warning = "SUICIDE"
        narrative = "This is certain death. The enemy force is overwhelming."
    elif ratio < 0.5:
        warning = "EXTREME"
        narrative = "This fight looks unwinnable. You'll need a miracle or an escape plan."
    elif ratio < 0.7:
        warning = "HIGH"
        narrative = "The odds are stacked against you. Consider retreat or finding allies."
    elif ratio < 0.9:
        warning = "MODERATE"
        narrative = "You're at a disadvantage, but skill and luck could see you through."
    elif ratio < 1.1:
        warning = "FAIR"
        narrative = "An even fight. Victory will come down to tactics and fortune."
    elif ratio < 1.5:
        warning = "FAVORABLE"
        narrative = "You have the advantage. Press it."
    else:
        warning = "OVERWHELMING"
        narrative = "They don't stand a chance."
    
    result["warning"] = warning
    result["narrative"] = narrative
    result["player_force"] = force_a.name
    result["enemy_force"] = force_b.name
    
    return result


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_combat_check(
    player_strength: float,
    player_count: int,
    enemy_strength: float,
    enemy_count: int,
    is_ranged: bool = True,
) -> dict:
    """
    Quick combat fairness check without building full force objects.
    
    Args:
        player_strength: Player's average attack power
        player_count: Number of player-side combatants
        enemy_strength: Enemy's average attack power
        enemy_count: Number of enemies
        is_ranged: True for ranged combat (square law)
        
    Returns:
        Warning dict with narrative context
    """
    player_force = CombatForce(
        name="Player",
        units=[CombatUnit(
            name="Player Team",
            count=player_count,
            attack_power=player_strength,
            is_ranged=is_ranged,
        )],
    )
    
    enemy_force = CombatForce(
        name="Enemy",
        units=[CombatUnit(
            name="Enemy Group",
            count=enemy_count,
            attack_power=enemy_strength,
            is_ranged=is_ranged,
        )],
    )
    
    force_type = ForceType.SQUARE if is_ranged else ForceType.LINEAR
    return predict_combat_outcome(player_force, enemy_force, force_type)


def get_combat_warning_context(prediction: dict) -> str:
    """
    Generate narrator context from combat prediction.
    
    Args:
        prediction: Result from predict_combat_outcome
        
    Returns:
        Context string for narrator prompt
    """
    lines = ["[COMBAT ASSESSMENT]"]
    
    warning = prediction.get("warning", "UNKNOWN")
    narrative = prediction.get("narrative", "")
    
    if warning in ["SUICIDE", "EXTREME"]:
        lines.append(f"⚠️ DANGER: {narrative}")
        lines.append("The player should be warned this fight is unfair.")
    elif warning == "HIGH":
        lines.append(f"⚠️ CAUTION: {narrative}")
    elif warning == "FAIR":
        lines.append(f"⚔️ {narrative}")
    elif warning in ["FAVORABLE", "OVERWHELMING"]:
        lines.append(f"✓ {narrative}")
    
    ratio = prediction.get("ratio", 1.0)
    if ratio < 1.0:
        lines.append(f"Force ratio: {ratio:.1%} (disadvantage)")
    else:
        lines.append(f"Force ratio: {ratio:.1%} (advantage)")
    
    return "\n".join(lines)


# ============================================================================
# Survival Estimation
# ============================================================================

def estimate_casualties(
    force_a: CombatForce,
    force_b: CombatForce,
    rounds: int = 5,
) -> dict:
    """
    Estimate casualties over multiple combat rounds.
    
    Uses Lanchester's differential equations in discrete form.
    
    Args:
        force_a: First force
        force_b: Second force
        rounds: Number of combat rounds to simulate
        
    Returns:
        Dict with estimated casualties and survivor counts
    """
    a_count = float(force_a.total_count)
    b_count = float(force_b.total_count)
    a_attack = force_a.average_attack * force_a.terrain_bonus
    b_attack = force_b.average_attack * force_b.terrain_bonus
    
    for _ in range(rounds):
        # Each side inflicts casualties proportional to their attack * count
        a_losses = min(a_count, b_attack * b_count * 0.1)
        b_losses = min(b_count, a_attack * a_count * 0.1)
        
        a_count = max(0, a_count - a_losses)
        b_count = max(0, b_count - b_losses)
        
        if a_count <= 0 or b_count <= 0:
            break
    
    return {
        "force_a_survivors": int(a_count),
        "force_b_survivors": int(b_count),
        "force_a_casualties": force_a.total_count - int(a_count),
        "force_b_casualties": force_b.total_count - int(b_count),
        "rounds_simulated": rounds,
        "decisive": a_count <= 0 or b_count <= 0,
    }
