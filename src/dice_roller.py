"""
Dice rolling utilities for multiple systems.

Includes deterministic support for advantage/disadvantage rolls,
critical result handling, and probability calculators.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Sequence


class AdvantageState(Enum):
    """Supported roll modes."""

    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


@dataclass
class RollSummary:
    """Structured result of a roll."""

    system: str
    rolls: List[int]
    kept: List[int]
    modifier: int
    total: int
    target: Optional[int]
    outcome: str
    critical: Optional[str] = None


# Comment: Critical handling was inconsistent between roll systems. Resolution (code change):
# apply shared override helpers below.

def _validate_fixed_rolls(fixed_roll: Optional[Sequence[int]], expected: int) -> Optional[List[int]]:
    if fixed_roll is None:
        return None
    if len(fixed_roll) != expected:
        raise ValueError(f"Expected {expected} fixed rolls, got {len(fixed_roll)}")
    return list(fixed_roll)


def _pull_die(fixed_rolls: Optional[List[int]], sides: int) -> int:
    if fixed_rolls is None:
        return random.randint(1, sides)
    return fixed_rolls.pop(0)


def _apply_critical_overrides(system: str, kept: List[int], total: int, target: Optional[int]) -> tuple[str, Optional[str]]:
    critical: Optional[str] = None
    outcome = None

    if system == "d20":
        die = kept[0]
        if die == 20:
            critical = "critical_success"
            outcome = "strong_hit"
        elif die == 1:
            critical = "critical_failure"
            outcome = "miss"
        else:
            outcome = "strong_hit" if target is not None and total >= target else "miss"
    elif system == "pbta":
        if len(kept) >= 2 and kept[0] == kept[1] == 6:
            critical = "critical_success"
            outcome = "strong_hit"
        elif len(kept) >= 2 and kept[0] == kept[1] == 1:
            critical = "critical_failure"
            outcome = "miss"
    return outcome, critical


# Comment: Advantage/disadvantage rolls with fixed inputs must stay deterministic. Resolution (code change):
# consume fixed rolls in order before any random generation.
def roll_d20(
    target: int,
    modifier: int = 0,
    advantage_state: AdvantageState = AdvantageState.NORMAL,
    fixed_roll: Optional[Sequence[int]] = None,
) -> RollSummary:
    if target < 1:
        raise ValueError("Target must be at least 1")

    dice_needed = 2 if advantage_state != AdvantageState.NORMAL else 1
    fixed = _validate_fixed_rolls(fixed_roll, dice_needed)

    rolls = [_pull_die(fixed, 20) for _ in range(dice_needed)]
    kept_value = (
        max(rolls)
        if advantage_state == AdvantageState.ADVANTAGE
        else min(rolls)
        if advantage_state == AdvantageState.DISADVANTAGE
        else rolls[0]
    )
    kept = [kept_value]
    total = kept_value + modifier

    outcome, critical = _apply_critical_overrides("d20", kept, total, target)
    if outcome is None:
        outcome = "strong_hit" if total >= target else "miss"

    return RollSummary(
        system="d20",
        rolls=rolls,
        kept=kept,
        modifier=modifier,
        total=total,
        target=target,
        outcome=outcome,
        critical=critical,
    )


def roll_pbta(
    modifier: int = 0,
    advantage_state: AdvantageState = AdvantageState.NORMAL,
    fixed_roll: Optional[Sequence[int]] = None,
) -> RollSummary:
    dice_needed = 3 if advantage_state != AdvantageState.NORMAL else 2
    fixed = _validate_fixed_rolls(fixed_roll, dice_needed)

    rolls = [_pull_die(fixed, 6) for _ in range(dice_needed)]
    sorted_rolls = sorted(rolls, reverse=True)
    if advantage_state == AdvantageState.ADVANTAGE:
        kept = sorted_rolls[:2]
    elif advantage_state == AdvantageState.DISADVANTAGE:
        kept = sorted(rolls)[:2]
    else:
        kept = rolls

    total = sum(kept) + modifier

    outcome, critical = _apply_critical_overrides("pbta", kept, total, None)
    if outcome is None:
        if total >= 10:
            outcome = "strong_hit"
        elif total >= 7:
            outcome = "weak_hit"
        else:
            outcome = "miss"

    return RollSummary(
        system="pbta",
        rolls=rolls,
        kept=kept,
        modifier=modifier,
        total=total,
        target=None,
        outcome=outcome,
        critical=critical,
    )


# Comment: Probability outputs should mirror UI display rounding. Resolution (docstring): rounding
# to four decimal places ensures percentages align with on-screen values.
def calculate_d20_probability(
    target: int,
    modifier: int = 0,
    advantage_state: AdvantageState = AdvantageState.NORMAL,
) -> dict[str, float]:
    if target < 1:
        raise ValueError("Target must be at least 1")

    total_outcomes = 20 if advantage_state == AdvantageState.NORMAL else 400
    success = miss = 0
    crit_success = crit_failure = 0

    if advantage_state == AdvantageState.NORMAL:
        for die in range(1, 21):
            kept = die
            total = kept + modifier
            if kept == 20:
                success += 1
                crit_success += 1
            elif kept == 1:
                miss += 1
                crit_failure += 1
            elif total >= target:
                success += 1
            else:
                miss += 1
    else:
        dice = itertools.product(range(1, 21), repeat=2)
        for d1, d2 in dice:
            kept = max(d1, d2) if advantage_state == AdvantageState.ADVANTAGE else min(d1, d2)
            total = kept + modifier
            if kept == 20:
                success += 1
                crit_success += 1
            elif kept == 1:
                miss += 1
                crit_failure += 1
            elif total >= target:
                success += 1
            else:
                miss += 1

    return {
        "strong_hit": round(success / total_outcomes, 4),
        "miss": round(miss / total_outcomes, 4),
        "critical_success": round(crit_success / total_outcomes, 4),
        "critical_failure": round(crit_failure / total_outcomes, 4),
    }


def calculate_pbta_probability(
    modifier: int = 0,
    advantage_state: AdvantageState = AdvantageState.NORMAL,
) -> dict[str, float]:
    dice_count = 3 if advantage_state != AdvantageState.NORMAL else 2
    total_outcomes = 6 ** dice_count
    strong = weak = miss = 0
    crit_success = crit_failure = 0

    dice = itertools.product(range(1, 7), repeat=dice_count)
    for roll in dice:
        if advantage_state == AdvantageState.ADVANTAGE:
            kept = sorted(roll, reverse=True)[:2]
        elif advantage_state == AdvantageState.DISADVANTAGE:
            kept = sorted(roll)[:2]
        else:
            kept = roll
        total = sum(kept) + modifier

        outcome, critical = _apply_critical_overrides("pbta", list(kept), total, None)
        if outcome is None:
            if total >= 10:
                outcome = "strong_hit"
            elif total >= 7:
                outcome = "weak_hit"
            else:
                outcome = "miss"

        if outcome == "strong_hit":
            strong += 1
        elif outcome == "weak_hit":
            weak += 1
        else:
            miss += 1

        if critical == "critical_success":
            crit_success += 1
        elif critical == "critical_failure":
            crit_failure += 1

    return {
        "strong_hit": round(strong / total_outcomes, 4),
        "weak_hit": round(weak / total_outcomes, 4),
        "miss": round(miss / total_outcomes, 4),
        "critical_success": round(crit_success / total_outcomes, 4),
        "critical_failure": round(crit_failure / total_outcomes, 4),
    }
