import pytest

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


def test_disco_probability_includes_modifiers():
    # Skill 2 with +3 modifiers effectively rolls at +5 and needs an 8+ on 2d6.
    probability = disco_success_probability(skill=2, difficulty=13, modifiers=3)
    assert probability == round(15 / 36, 4)


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


def test_baldurs_gate_probability_handles_cancelled_advantage():
    straight = baldurs_gate_success_probability(modifier=5, dc=12)
    cancelled = baldurs_gate_success_probability(modifier=5, dc=12, advantage=True, disadvantage=True)
    assert straight == cancelled


def test_roll_helpers_return_structured_results():
    disco = roll_disco_check(skill=2, difficulty=10, modifiers=1, fixed_dice=(5, 4))
    assert disco.dice == (5, 4)
    assert disco.total == 12
    assert disco.success is True
    assert disco.is_critical_success is False
    assert disco.is_critical_failure is False

    bg3 = roll_baldurs_gate_check(modifier=3, dc=12, advantage=True, fixed_rolls=(7, 9))
    assert bg3.dice == (7, 9)
    assert bg3.total == 12
    assert bg3.success is True
    assert bg3.applied_advantage is True
    assert bg3.applied_disadvantage is False


def test_fixed_dice_validation():
    with pytest.raises(ValueError):
        roll_disco_check(skill=1, difficulty=5, fixed_dice=(1,))
    with pytest.raises(ValueError):
        roll_disco_check(skill=1, difficulty=5, fixed_dice=(7, 2))

    with pytest.raises(ValueError):
        roll_baldurs_gate_check(modifier=0, dc=10, fixed_rolls=(1, 2, 3))
    with pytest.raises(ValueError):
        roll_baldurs_gate_check(modifier=0, dc=10, advantage=True, fixed_rolls=(0, 20))
    with pytest.raises(ValueError):
        roll_baldurs_gate_check(modifier=0, dc=10, disadvantage=True, fixed_rolls=(1,))


def test_fixed_rolls_require_single_value_when_advantage_cancels():
    with pytest.raises(ValueError):
        roll_baldurs_gate_check(modifier=0, dc=10, advantage=True, disadvantage=True, fixed_rolls=(5, 15))

    result = roll_baldurs_gate_check(modifier=2, dc=12, advantage=True, disadvantage=True, fixed_rolls=(10,))
    assert result.dice == (10,)
    assert result.applied_advantage is False
    assert result.applied_disadvantage is False
    assert result.success is True


def test_disco_fixed_dice_respect_critical_overrides():
    critical_fail = roll_disco_check(skill=20, difficulty=2, fixed_dice=(1, 1))
    assert critical_fail.success is False
    assert critical_fail.is_critical_failure is True

    critical_success = roll_disco_check(skill=0, difficulty=20, fixed_dice=(6, 6))
    assert critical_success.success is True
    assert critical_success.is_critical_success is True


def test_baldurs_gate_fixed_rolls_use_advantage_and_disadvantage_rules():
    advantaged = roll_baldurs_gate_check(modifier=0, dc=10, advantage=True, fixed_rolls=(2, 18))
    assert advantaged.dice == (2, 18)
    assert advantaged.applied_advantage is True
    assert advantaged.total == 18
    assert advantaged.success is True

    disadvantaged = roll_baldurs_gate_check(modifier=0, dc=15, disadvantage=True, fixed_rolls=(17, 4))
    assert disadvantaged.dice == (17, 4)
    assert disadvantaged.applied_disadvantage is True
    assert disadvantaged.total == 4
    assert disadvantaged.success is False


def test_baldurs_gate_natural_one_still_fails_with_large_bonus():
    result = roll_baldurs_gate_check(modifier=15, dc=16, fixed_rolls=(1,))
    assert result.total == 16
    assert result.is_critical_failure is True
    assert result.success is False


def test_baldurs_gate_natural_twenty_overrides_high_dc():
    result = roll_baldurs_gate_check(modifier=-2, dc=25, fixed_rolls=(20,))
    assert result.total == 18
    assert result.is_critical_success is True
    assert result.success is True


def test_disco_probability_supports_negative_modifiers():
    # Skill 3 with -2 modifiers rolls as +1 and needs 11+ on 2d6.
    probability = disco_success_probability(skill=3, difficulty=12, modifiers=-2)
    assert probability == round(3 / 36, 4)


def test_baldurs_gate_probability_has_natural_twenty_floor():
    # With an extreme DC, only a natural 20 should succeed.
    probability = baldurs_gate_success_probability(modifier=-5, dc=30)
    assert probability == 0.05
