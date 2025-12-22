"""Skill check helpers inspired by Disco Elysium and Baldur's Gate 3.

This module provides reusable helpers for bell-curve (2d6) and linear (d20)
skill checks. The focus is on transparency and testability so the calling code
can expose exact odds to the player before a roll is made.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable


def _roll_die(sides: int) -> int:
    return random.randint(1, sides)


@dataclass
class DiscoElysiumResult:
    """Outcome of a Disco Elysium-style active check."""

    dice: tuple[int, int]
    total: int
    success: bool
    is_critical_success: bool
    is_critical_failure: bool


def roll_disco_check(skill: int, difficulty: int, modifiers: int = 0) -> DiscoElysiumResult:
    """Roll a Disco Elysium-inspired 2d6 skill check.

    Critical results override normal resolution:
    - Double sixes are an automatic success.
    - Double ones are an automatic failure.
    """

    d1, d2 = _roll_die(6), _roll_die(6)
    total = d1 + d2 + skill + modifiers

    is_double_six = d1 == d2 == 6
    is_double_one = d1 == d2 == 1

    is_success = total >= difficulty or is_double_six
    if is_double_one:
        is_success = False

    return DiscoElysiumResult(
        dice=(d1, d2),
        total=total,
        success=is_success,
        is_critical_success=is_double_six,
        is_critical_failure=is_double_one,
    )


def disco_success_probability(skill: int, difficulty: int, modifiers: int = 0) -> float:
    """Calculate exact success probability for a Disco Elysium-style check."""

    success = 0
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            total = d1 + d2 + skill + modifiers
            is_double_six = d1 == d2 == 6
            is_double_one = d1 == d2 == 1

            roll_success = (total >= difficulty) or is_double_six
            if is_double_one:
                roll_success = False
            if roll_success:
                success += 1

    return round(success / 36, 4)


@dataclass
class BaldursGateResult:
    """Outcome of a Baldur's Gate 3-style ability check."""

    dice: tuple[int, ...]
    total: int
    success: bool
    is_critical_success: bool
    is_critical_failure: bool
    applied_advantage: bool
    applied_disadvantage: bool


def _d20_pool(advantage: bool, disadvantage: bool) -> Iterable[tuple[int, ...]]:
    """Return all possible d20 pools for advantage/disadvantage scenarios."""

    if advantage and disadvantage:
        # They cancel out to a single die.
        return ((roll,) for roll in range(1, 21))
    if advantage:
        return ((d1, d2) for d1 in range(1, 21) for d2 in range(1, 21))
    if disadvantage:
        return ((d1, d2) for d1 in range(1, 21) for d2 in range(1, 21))
    return ((roll,) for roll in range(1, 21))


def roll_baldurs_gate_check(
    modifier: int,
    dc: int,
    advantage: bool = False,
    disadvantage: bool = False,
) -> BaldursGateResult:
    """Roll a Baldur's Gate 3-style check with optional advantage.

    Natural 20 is an automatic success and natural 1 is an automatic failure.
    """

    dice: tuple[int, ...]
    if advantage and disadvantage:
        dice = (_roll_die(20),)
    elif advantage:
        dice = (_roll_die(20), _roll_die(20))
    elif disadvantage:
        dice = (_roll_die(20), _roll_die(20))
    else:
        dice = (_roll_die(20),)

    if advantage and not disadvantage:
        roll_value = max(dice)
    elif disadvantage and not advantage:
        roll_value = min(dice)
    else:
        roll_value = dice[0]

    total = roll_value + modifier
    is_nat_20 = roll_value == 20
    is_nat_1 = roll_value == 1

    is_success = total >= dc or is_nat_20
    if is_nat_1:
        is_success = False

    return BaldursGateResult(
        dice=dice,
        total=total,
        success=is_success,
        is_critical_success=is_nat_20,
        is_critical_failure=is_nat_1,
        applied_advantage=advantage and not disadvantage,
        applied_disadvantage=disadvantage and not advantage,
    )


def baldurs_gate_success_probability(
    modifier: int, dc: int, advantage: bool = False, disadvantage: bool = False
) -> float:
    """Calculate exact success probability for Baldur's Gate 3-style checks."""

    success = 0
    total_outcomes = 0

    for dice in _d20_pool(advantage, disadvantage):
        total_outcomes += 1

        if advantage and not disadvantage:
            roll_value = max(dice)
        elif disadvantage and not advantage:
            roll_value = min(dice)
        else:
            roll_value = dice[0]

        is_nat_20 = roll_value == 20
        is_nat_1 = roll_value == 1

        roll_success = (roll_value + modifier >= dc) or is_nat_20
        if is_nat_1:
            roll_success = False

        if roll_success:
            success += 1

    return round(success / total_outcomes, 4)
