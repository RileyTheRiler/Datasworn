"""
Starforged Rules Engine.
Implements dice mechanics: Action Rolls, Progress Rolls, and Momentum.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class RollResult(Enum):
    """Possible outcomes of a roll."""
    STRONG_HIT = "Strong Hit"
    WEAK_HIT = "Weak Hit"
    MISS = "Miss"


@dataclass
class ActionRollResult:
    """Complete result of an Action Roll."""
    action_die: int
    stat: int
    adds: int
    action_score: int
    challenge_dice: tuple[int, int]
    result: RollResult
    is_match: bool

    def __str__(self) -> str:
        match_str = " (MATCH!)" if self.is_match else ""
        return (
            f"{self.result.value}{match_str}\n"
            f"Action: d6({self.action_die}) + {self.stat} + {self.adds} = {self.action_score}\n"
            f"Challenge: d10({self.challenge_dice[0]}) vs d10({self.challenge_dice[1]})"
        )


@dataclass
class ProgressRollResult:
    """Complete result of a Progress Roll."""
    progress: int
    challenge_dice: tuple[int, int]
    result: RollResult
    is_match: bool

    def __str__(self) -> str:
        match_str = " (MATCH!)" if self.is_match else ""
        return (
            f"{self.result.value}{match_str}\n"
            f"Progress: {self.progress} vs Challenge: "
            f"d10({self.challenge_dice[0]}) & d10({self.challenge_dice[1]})"
        )


Rank = Literal["troublesome", "dangerous", "formidable", "extreme", "epic"]

RANK_PROGRESS: dict[Rank, int] = {
    "troublesome": 12,  # 3 boxes (12 ticks)
    "dangerous": 8,     # 2 boxes (8 ticks)
    "formidable": 4,    # 1 box (4 ticks)
    "extreme": 2,       # half box
    "epic": 1,          # quarter box
}


@dataclass
class ProgressTrack:
    """
    Represents a progress track (Vow, Expedition, Combat, etc.).
    10 boxes, each with 4 ticks = 40 total ticks.
    """
    name: str
    rank: Rank
    ticks: int = 0
    completed: bool = False

    @property
    def boxes(self) -> int:
        """Number of fully filled boxes (0-10)."""
        return min(self.ticks // 4, 10)

    @property
    def display(self) -> str:
        """Visual representation of the track."""
        full = self.boxes
        partial_ticks = self.ticks % 4
        empty = 10 - full - (1 if partial_ticks > 0 else 0)
        partial = "▓" if partial_ticks > 0 else ""
        return f"[{'█' * full}{partial}{'░' * empty}] {self.boxes}/10"

    def mark_progress(self, times: int = 1) -> int:
        """Mark progress based on rank. Returns new tick count."""
        ticks_to_add = RANK_PROGRESS[self.rank] * times
        self.ticks = min(self.ticks + ticks_to_add, 40)
        return self.ticks

    def progress_roll(self) -> ProgressRollResult:
        """Make a progress roll against this track."""
        d1 = random.randint(1, 10)
        d2 = random.randint(1, 10)
        is_match = d1 == d2
        progress = self.boxes

        if progress > d1 and progress > d2:
            result = RollResult.STRONG_HIT
        elif progress > d1 or progress > d2:
            result = RollResult.WEAK_HIT
        else:
            result = RollResult.MISS

        return ProgressRollResult(
            progress=progress,
            challenge_dice=(d1, d2),
            result=result,
            is_match=is_match,
        )


@dataclass
class Momentum:
    """Manages momentum mechanics."""
    value: int = 2
    max_value: int = 10
    reset_value: int = 2
    min_value: int = -6

    def gain(self, amount: int = 1) -> int:
        """Gain momentum (capped at max)."""
        self.value = min(self.value + amount, self.max_value)
        return self.value

    def lose(self, amount: int = 1) -> int:
        """Lose momentum (floored at min)."""
        self.value = max(self.value - amount, self.min_value)
        return self.value

    def reset(self) -> int:
        """Reset momentum after burning."""
        self.value = self.reset_value
        return self.value

    def can_burn(self, challenge_dice: tuple[int, int]) -> bool:
        """Check if momentum can be burned to improve outcome."""
        if self.value <= 0:
            return False
        # Can burn if momentum beats at least one challenge die
        return self.value > challenge_dice[0] or self.value > challenge_dice[1]

    def burn(
        self, original_result: RollResult, challenge_dice: tuple[int, int]
    ) -> RollResult | None:
        """
        Burn momentum to potentially improve the result.
        Returns the new result if burning is beneficial, None otherwise.
        """
        if not self.can_burn(challenge_dice):
            return None

        # Calculate what result we'd get with momentum as action score
        if self.value > challenge_dice[0] and self.value > challenge_dice[1]:
            new_result = RollResult.STRONG_HIT
        elif self.value > challenge_dice[0] or self.value > challenge_dice[1]:
            new_result = RollResult.WEAK_HIT
        else:
            return None

        # Only burn if it improves the result
        result_order = {RollResult.MISS: 0, RollResult.WEAK_HIT: 1, RollResult.STRONG_HIT: 2}
        if result_order[new_result] > result_order[original_result]:
            self.reset()
            return new_result
        return None


def action_roll(stat: int, adds: int = 0) -> ActionRollResult:
    """
    Perform an Action Roll.

    Args:
        stat: The character stat being used (1-3)
        adds: Additional modifiers (+1, +2, etc.)

    Returns:
        ActionRollResult with all dice values and outcome
    """
    action_die = random.randint(1, 6)
    action_score = action_die + stat + adds

    d1 = random.randint(1, 10)
    d2 = random.randint(1, 10)
    is_match = d1 == d2

    if action_score > d1 and action_score > d2:
        result = RollResult.STRONG_HIT
    elif action_score > d1 or action_score > d2:
        result = RollResult.WEAK_HIT
    else:
        result = RollResult.MISS

    return ActionRollResult(
        action_die=action_die,
        stat=stat,
        adds=adds,
        action_score=action_score,
        challenge_dice=(d1, d2),
        result=result,
        is_match=is_match,
    )


def calculate_probability(stat: int, adds: int = 0) -> dict[str, float]:
    """
    Calculate the exact probability of Strong Hit, Weak Hit, and Miss.
    Used for UI display before rolling (Disco Elysium style).
    """
    total_combinations = 6 * 10 * 10
    strong_hits = 0
    weak_hits = 0
    misses = 0

    # Iterate through all dice combinations
    for action_die in range(1, 7):
        action_score = action_die + stat + adds
        for d1 in range(1, 11):
            for d2 in range(1, 11):
                if action_score > d1 and action_score > d2:
                    strong_hits += 1
                elif action_score > d1 or action_score > d2:
                    weak_hits += 1
                else:
                    misses += 1
    
    return {
        "strong_hit": round(strong_hits / total_combinations, 3),
        "weak_hit": round(weak_hits / total_combinations, 3),
        "miss": round(misses / total_combinations, 3)
    }


def calculate_2d6_probability(modifier: int = 0) -> dict[str, float]:
    """
    Calculate PbtA-style probabilities for a 2d6 + modifier roll.

    Returns strong hits (10+), weak hits (7-9), and misses (6-).
    """
    strong_hits = 0
    weak_hits = 0
    misses = 0
    total_combinations = 6 * 6

    for d1 in range(1, 7):
        for d2 in range(1, 7):
            total = d1 + d2 + modifier
            if total >= 10:
                strong_hits += 1
            elif total >= 7:
                weak_hits += 1
            else:
                misses += 1

    return {
        "strong_hit": round(strong_hits / total_combinations, 3),
        "weak_hit": round(weak_hits / total_combinations, 3),
        "miss": round(misses / total_combinations, 3),
    }


def calculate_d20_probability(
    dc: int,
    modifier: int = 0,
    advantage: bool = False,
    disadvantage: bool = False,
    fixed_roll: int | None = None,
) -> dict[str, float]:
    """
    Calculate the probability of meeting/exceeding a DC on a d20 roll.

    Supports advantage/disadvantage and tracks natural 20/1 critical bands.
    When fixed_roll is provided, advantage/disadvantage are ignored and the
    function reports deterministic outcomes for that die result.
    """
    if advantage and disadvantage:
        raise ValueError("Cannot have both advantage and disadvantage")

    if fixed_roll is not None:
        rolls = [(fixed_roll, fixed_roll)] if (advantage or disadvantage) else [(fixed_roll,)]
    elif advantage or disadvantage:
        rolls = [
            (r1, r2)
            for r1 in range(1, 21)
            for r2 in range(1, 21)
        ]
    else:
        rolls = [(r,) for r in range(1, 21)]

    success = 0
    failure = 0
    crit_success = 0
    crit_failure = 0
    total_combinations = len(rolls)

    for result in rolls:
        if advantage:
            final = max(result)
        elif disadvantage:
            final = min(result)
        else:
            final = result[0]

        if final == 20:
            crit_success += 1
        if final == 1:
            crit_failure += 1

        if final + modifier >= dc:
            success += 1
        else:
            failure += 1

    return {
        "success": round(success / total_combinations, 3),
        "failure": round(failure / total_combinations, 3),
        "critical_success": round(crit_success / total_combinations, 3),
        "critical_failure": round(crit_failure / total_combinations, 3),
    }

