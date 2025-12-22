import random

from src.skill_checks import (
    baldurs_gate_success_probability,
    disco_success_probability,
    roll_baldurs_gate_check,
    roll_disco_check,
)


def test_disco_probability_matches_expected_mid_difficulty():
    # Skill 4 vs difficulty 10 should require a 6+ on 2d6 minus the snake eyes auto-fail.
    probability = disco_success_probability(skill=4, difficulty=10)
    assert probability == round(26 / 36, 4)


def test_disco_probability_handles_impossible_checks_with_crits():
    # Only double six should succeed here.
    probability = disco_success_probability(skill=0, difficulty=20)
    assert probability == round(1 / 36, 4)


def test_baldurs_gate_probability_without_advantage():
    probability = baldurs_gate_success_probability(modifier=5, dc=15)
    assert probability == 11 / 20


def test_baldurs_gate_probability_with_advantage_matches_bruteforce():
    probability = baldurs_gate_success_probability(modifier=0, dc=15, advantage=True)
    # Calculate by brute force to avoid hardcoding a fragile constant.
    success = 0
    total = 0
    for d1 in range(1, 21):
        for d2 in range(1, 21):
            total += 1
            roll = max(d1, d2)
            is_success = roll == 20 or (roll + 0 >= 15)
            if roll == 1:
                is_success = False
            if is_success:
                success += 1
    assert probability == round(success / total, 4)


def test_roll_helpers_return_structured_results():
    random.seed(42)
    disco = roll_disco_check(skill=2, difficulty=10, modifiers=1)
    assert disco.dice == (6, 1)
    assert disco.total == 10
    assert disco.success is True
    assert disco.is_critical_success is False
    assert disco.is_critical_failure is False

    bg3 = roll_baldurs_gate_check(modifier=3, dc=12, advantage=True)
    assert bg3.dice == (1, 9)
    assert bg3.total == 12
    assert bg3.success is True
    assert bg3.applied_advantage is True
    assert bg3.applied_disadvantage is False
