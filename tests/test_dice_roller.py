import pytest

from src.dice_roller import (
    AdvantageState,
    calculate_d20_probability,
    calculate_pbta_probability,
    roll_d20,
    roll_pbta,
)


@pytest.mark.parametrize(
    "fixed_roll,modifier,target,expected_outcome",
    [
        ([1], 10, 5, "miss"),  # natural 1 fails even when the math would succeed
        ([20], -5, 25, "strong_hit"),  # natural 20 succeeds despite modifier
    ],
)
def test_d20_critical_overrides_outcome(fixed_roll, modifier, target, expected_outcome):
    result = roll_d20(target=target, modifier=modifier, fixed_roll=fixed_roll)
    assert result.outcome == expected_outcome
    assert result.critical is not None


def test_pbta_critical_overrides_even_with_penalty():
    result = roll_pbta(modifier=-4, fixed_roll=[6, 6])
    assert result.outcome == "strong_hit"
    assert result.critical == "critical_success"


def test_advantage_disadvantage_selection_math():
    advantaged = roll_pbta(
        advantage_state=AdvantageState.ADVANTAGE,
        fixed_roll=[1, 2, 6],
    )
    assert advantaged.kept == [6, 2]
    assert advantaged.outcome == "weak_hit"

    disadvantaged = roll_pbta(
        advantage_state=AdvantageState.DISADVANTAGE,
        fixed_roll=[6, 5, 1],
    )
    assert disadvantaged.kept == [1, 5]
    assert disadvantaged.outcome == "miss"


def test_fixed_roll_is_deterministic_with_advantage():
    result = roll_d20(target=15, advantage_state=AdvantageState.ADVANTAGE, fixed_roll=[4, 15])
    assert result.kept == [15]
    assert result.outcome == "strong_hit"


def test_invalid_fixed_roll_length_raises():
    with pytest.raises(ValueError):
        roll_d20(target=10, advantage_state=AdvantageState.ADVANTAGE, fixed_roll=[5])


@pytest.mark.parametrize(
    "prob_func,kwargs,expected",
    [
        (
            calculate_d20_probability,
            {"target": 11},
            {"strong_hit": pytest.approx(0.5), "critical_success": pytest.approx(0.05)},
        ),
        (
            calculate_d20_probability,
            {"target": 11, "advantage_state": AdvantageState.ADVANTAGE},
            {"strong_hit": pytest.approx(0.75), "critical_success": pytest.approx(0.0975)},
        ),
        (
            calculate_pbta_probability,
            {},
            {
                "strong_hit": pytest.approx(0.1667),
                "weak_hit": pytest.approx(0.4167),
                "miss": pytest.approx(0.4167),
            },
        ),
        (
            calculate_pbta_probability,
            {"advantage_state": AdvantageState.ADVANTAGE},
            {
                "strong_hit": pytest.approx(0.3565),
                "weak_hit": pytest.approx(0.4491),
                "miss": pytest.approx(0.1944),
            },
        ),
    ],
)
def test_probability_calculators_match_known_values(prob_func, kwargs, expected):
    probabilities = prob_func(**kwargs)
    for key, matcher in expected.items():
        assert key in probabilities
        assert probabilities[key] == matcher


@pytest.mark.parametrize(
    "prob_func,kwargs",
    [
        (calculate_d20_probability, {"target": 0}),
        (calculate_d20_probability, {"target": -3}),
    ],
)
def test_probability_calculators_validate_inputs(prob_func, kwargs):
    with pytest.raises(ValueError):
        prob_func(**kwargs)
