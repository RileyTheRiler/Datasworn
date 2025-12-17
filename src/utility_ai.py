"""
Utility AI System for Tactical Decision Making.
NPCs score potential actions based on multiple weighted factors.

Based on Game AI Pro patterns for "fuzzy" decision making that creates
organic, non-binary behavior.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
import math


# ============================================================================
# Consideration Curves
# ============================================================================

class CurveType(Enum):
    """Types of response curves for considerations."""
    LINEAR = "linear"           # y = mx + b
    QUADRATIC = "quadratic"     # y = x^2 (or x^0.5 for sqrt)
    LOGISTIC = "logistic"       # S-curve, good for thresholds
    EXPONENTIAL = "exponential" # y = e^x, rapid growth
    INVERSE = "inverse"         # y = 1/x, diminishing returns


def apply_curve(value: float, curve: CurveType, slope: float = 1.0, offset: float = 0.0) -> float:
    """
    Apply a response curve to normalize a value to 0-1 range.
    
    Args:
        value: Input value (usually 0-1)
        curve: Type of curve to apply
        slope: Steepness multiplier
        offset: Shift the curve
    
    Returns:
        Transformed value in 0-1 range
    """
    # Clamp input
    value = max(0.0, min(1.0, value))
    
    if curve == CurveType.LINEAR:
        result = slope * value + offset
    
    elif curve == CurveType.QUADRATIC:
        result = math.pow(value, slope)  # slope < 1 = sqrt, slope > 1 = power
    
    elif curve == CurveType.LOGISTIC:
        # S-curve centered at 0.5
        k = slope * 10  # Make slope more impactful
        result = 1.0 / (1.0 + math.exp(-k * (value - 0.5)))
    
    elif curve == CurveType.EXPONENTIAL:
        result = (math.exp(slope * value) - 1) / (math.exp(slope) - 1)
    
    elif curve == CurveType.INVERSE:
        # Avoid division by zero
        result = 1.0 / (1.0 + (1.0 - value) * slope)
    
    else:
        result = value
    
    # Clamp output to 0-1
    return max(0.0, min(1.0, result + offset))


# ============================================================================
# Considerations
# ============================================================================

@dataclass
class Consideration:
    """
    A single factor that influences action scoring.
    
    Examples:
        - "my health is low" → flee becomes more attractive
        - "enemy is close" → attack becomes more attractive
        - "I have cover nearby" → take_cover becomes viable
    """
    name: str
    input_getter: Callable[[dict], float]  # Returns 0-1 value from context
    curve: CurveType = CurveType.LINEAR
    slope: float = 1.0
    offset: float = 0.0
    weight: float = 1.0  # How important this consideration is
    
    def evaluate(self, context: dict) -> float:
        """Evaluate this consideration given the context."""
        raw_value = self.input_getter(context)
        curved_value = apply_curve(raw_value, self.curve, self.slope, self.offset)
        return curved_value * self.weight


# ============================================================================
# Pre-built Considerations
# ============================================================================

# Health-based considerations
HEALTH_LOW = Consideration(
    name="health_low",
    input_getter=lambda ctx: 1.0 - ctx.get("health", 1.0),  # Inverse: low health = high value
    curve=CurveType.QUADRATIC,
    slope=2.0,  # Rapidly increases as health drops
    weight=1.5,
)

HEALTH_HIGH = Consideration(
    name="health_high",
    input_getter=lambda ctx: ctx.get("health", 1.0),
    curve=CurveType.LINEAR,
    weight=1.0,
)

# Threat-based considerations
THREAT_HIGH = Consideration(
    name="threat_high",
    input_getter=lambda ctx: ctx.get("threat_level", 0.0),
    curve=CurveType.LOGISTIC,
    slope=1.5,  # Sharp increase around 0.5
    weight=1.3,
)

THREAT_LOW = Consideration(
    name="threat_low",
    input_getter=lambda ctx: 1.0 - ctx.get("threat_level", 0.0),
    curve=CurveType.LINEAR,
    weight=0.8,
)

# Resource considerations
AMMO_AVAILABLE = Consideration(
    name="ammo_available",
    input_getter=lambda ctx: ctx.get("ammo", 1.0),
    curve=CurveType.QUADRATIC,
    slope=0.5,  # sqrt curve - even some ammo is useful
    weight=1.0,
)

AMMO_LOW = Consideration(
    name="ammo_low",
    input_getter=lambda ctx: 1.0 - ctx.get("ammo", 1.0),
    curve=CurveType.EXPONENTIAL,
    slope=2.0,
    weight=1.2,
)

# Tactical considerations
HAS_COVER = Consideration(
    name="has_cover",
    input_getter=lambda ctx: 1.0 if ctx.get("cover_nearby", False) else 0.0,
    curve=CurveType.LINEAR,
    weight=1.0,
)

NO_COVER = Consideration(
    name="no_cover",
    input_getter=lambda ctx: 0.0 if ctx.get("cover_nearby", False) else 1.0,
    curve=CurveType.LINEAR,
    weight=0.8,
)

# Ally considerations
HAS_ALLIES = Consideration(
    name="has_allies",
    input_getter=lambda ctx: min(1.0, ctx.get("allies_nearby", 0) / 3.0),  # Cap at 3 allies
    curve=CurveType.QUADRATIC,
    slope=0.7,
    weight=1.1,
)

ALONE = Consideration(
    name="alone",
    input_getter=lambda ctx: 1.0 if ctx.get("allies_nearby", 0) == 0 else 0.0,
    curve=CurveType.LINEAR,
    weight=1.0,
)

# Distance considerations
ENEMY_CLOSE = Consideration(
    name="enemy_close",
    input_getter=lambda ctx: 1.0 - ctx.get("enemy_distance", 0.5),  # 0 = adjacent, 1 = far
    curve=CurveType.EXPONENTIAL,
    slope=1.5,
    weight=1.2,
)

ENEMY_FAR = Consideration(
    name="enemy_far",
    input_getter=lambda ctx: ctx.get("enemy_distance", 0.5),
    curve=CurveType.LINEAR,
    weight=0.9,
)


# ============================================================================
# Tactical Actions
# ============================================================================

@dataclass
class TacticalAction:
    """
    A possible action with its considerations.
    Final score = average of all consideration scores * base_weight
    """
    name: str
    considerations: list[Consideration] = field(default_factory=list)
    base_weight: float = 1.0
    description: str = ""
    
    def score(self, context: dict) -> float:
        """Calculate the utility score for this action."""
        if not self.considerations:
            return self.base_weight * 0.5  # Default score
        
        # Multiplicative scoring (one bad factor tanks the whole action)
        # This prevents actions with one great score but others at 0
        total = 1.0
        for consideration in self.considerations:
            factor = consideration.evaluate(context)
            # Slight boost to prevent complete zeroing
            total *= (factor + 0.1) / 1.1
        
        return total * self.base_weight


# Pre-built tactical actions
ATTACK_ACTION = TacticalAction(
    name="attack",
    considerations=[HEALTH_HIGH, AMMO_AVAILABLE, ENEMY_CLOSE, THREAT_LOW],
    base_weight=1.0,
    description="Engage the enemy directly",
)

FLEE_ACTION = TacticalAction(
    name="flee",
    considerations=[HEALTH_LOW, THREAT_HIGH, ALONE, AMMO_LOW],
    base_weight=0.8,  # Slightly lower base - NPCs shouldn't flee too readily
    description="Retreat from combat",
)

TAKE_COVER_ACTION = TacticalAction(
    name="take_cover",
    considerations=[HAS_COVER, THREAT_HIGH, HEALTH_LOW, AMMO_AVAILABLE],
    base_weight=1.1,
    description="Move to cover and fight defensively",
)

ADVANCE_ACTION = TacticalAction(
    name="advance",
    considerations=[HEALTH_HIGH, AMMO_AVAILABLE, THREAT_LOW, HAS_ALLIES],
    base_weight=0.9,
    description="Push forward toward the objective",
)

FLANK_ACTION = TacticalAction(
    name="flank",
    considerations=[HEALTH_HIGH, AMMO_AVAILABLE, HAS_ALLIES, ENEMY_FAR],
    base_weight=1.2,  # Flanking is smart when possible
    description="Circle around to attack from the side",
)

HOLD_POSITION_ACTION = TacticalAction(
    name="hold_position",
    considerations=[HAS_COVER, AMMO_AVAILABLE, THREAT_HIGH],
    base_weight=0.85,
    description="Stay in current position and defend",
)

CALL_REINFORCEMENTS_ACTION = TacticalAction(
    name="call_reinforcements",
    considerations=[ALONE, THREAT_HIGH, HEALTH_LOW],
    base_weight=1.3,  # Smart choice when available
    description="Call for backup",
)


# ============================================================================
# Utility AI System
# ============================================================================

@dataclass 
class UtilityAI:
    """
    Utility-based AI decision maker.
    Evaluates all actions and picks the best one.
    """
    actions: list[TacticalAction] = field(default_factory=list)
    randomness: float = 0.1  # Add some unpredictability
    
    def evaluate(self, context: dict) -> tuple[str, float, list[tuple[str, float]]]:
        """
        Evaluate all actions and return the best one.
        
        Returns:
            Tuple of (best_action_name, best_score, all_scores)
        """
        import random
        
        scores = []
        for action in self.actions:
            base_score = action.score(context)
            # Add controlled randomness
            if self.randomness > 0:
                noise = random.uniform(-self.randomness, self.randomness)
                final_score = max(0, base_score + noise)
            else:
                final_score = base_score
            scores.append((action.name, final_score, action.description))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        if scores:
            best_name, best_score, best_desc = scores[0]
            return best_name, best_score, [(n, s) for n, s, _ in scores]
        
        return "idle", 0.0, []


# ============================================================================
# Pre-built AI Profiles
# ============================================================================

def create_combat_ai() -> UtilityAI:
    """Standard combat AI with balanced tactics."""
    return UtilityAI(
        actions=[
            ATTACK_ACTION,
            TAKE_COVER_ACTION,
            FLEE_ACTION,
            ADVANCE_ACTION,
            HOLD_POSITION_ACTION,
        ],
        randomness=0.1,
    )


def create_aggressive_ai() -> UtilityAI:
    """Aggressive AI that prioritizes attack."""
    attack = TacticalAction(
        name="attack",
        considerations=[HEALTH_HIGH, AMMO_AVAILABLE, ENEMY_CLOSE],
        base_weight=1.5,  # Much higher attack preference
    )
    return UtilityAI(
        actions=[
            attack,
            ADVANCE_ACTION,
            FLANK_ACTION,
            HOLD_POSITION_ACTION,
        ],
        randomness=0.15,  # More erratic
    )


def create_cautious_ai() -> UtilityAI:
    """Cautious AI that prioritizes survival."""
    return UtilityAI(
        actions=[
            TAKE_COVER_ACTION,
            HOLD_POSITION_ACTION,
            FLEE_ACTION,
            ATTACK_ACTION,
            CALL_REINFORCEMENTS_ACTION,
        ],
        randomness=0.05,  # More predictable
    )


def create_squad_leader_ai() -> UtilityAI:
    """Squad leader that coordinates and supports."""
    return UtilityAI(
        actions=[
            CALL_REINFORCEMENTS_ACTION,
            TacticalAction(
                name="direct_allies",
                considerations=[HAS_ALLIES, THREAT_HIGH],
                base_weight=1.4,
                description="Coordinate ally actions",
            ),
            HOLD_POSITION_ACTION,
            TAKE_COVER_ACTION,
            ATTACK_ACTION,
        ],
        randomness=0.08,
    )


# ============================================================================
# Convenience Functions
# ============================================================================

def evaluate_tactical_decision(
    health: float = 1.0,
    threat_level: float = 0.5,
    ammo: float = 1.0,
    cover_nearby: bool = False,
    allies_nearby: int = 0,
    enemy_distance: float = 0.5,
    ai_profile: str = "balanced",
) -> dict:
    """
    Evaluate a tactical decision for an NPC.
    
    Args:
        health: 0-1 health ratio
        threat_level: 0-1 perceived danger
        ammo: 0-1 ammunition ratio
        cover_nearby: Whether cover is available
        allies_nearby: Number of allies in range
        enemy_distance: 0-1 distance to enemy (0=close, 1=far)
        ai_profile: "balanced", "aggressive", "cautious", "leader"
    
    Returns:
        Dict with action, score, reasoning, and all_scores
    """
    context = {
        "health": health,
        "threat_level": threat_level,
        "ammo": ammo,
        "cover_nearby": cover_nearby,
        "allies_nearby": allies_nearby,
        "enemy_distance": enemy_distance,
    }
    
    # Select AI profile
    if ai_profile == "aggressive":
        ai = create_aggressive_ai()
    elif ai_profile == "cautious":
        ai = create_cautious_ai()
    elif ai_profile == "leader":
        ai = create_squad_leader_ai()
    else:
        ai = create_combat_ai()
    
    best_action, best_score, all_scores = ai.evaluate(context)
    
    # Generate reasoning
    reasoning = []
    if health < 0.3:
        reasoning.append("critically wounded")
    elif health < 0.6:
        reasoning.append("injured")
    if threat_level > 0.7:
        reasoning.append("facing heavy fire")
    if ammo < 0.2:
        reasoning.append("low on ammo")
    if allies_nearby == 0:
        reasoning.append("isolated")
    elif allies_nearby >= 2:
        reasoning.append("with squad support")
    
    return {
        "action": best_action,
        "score": best_score,
        "reasoning": ", ".join(reasoning) if reasoning else "standard engagement",
        "all_scores": all_scores,
    }
