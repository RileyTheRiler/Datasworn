# Dice Mechanics and Probabilities Overview

## Public Functions

### `action_roll(stat: int, adds: int = 0) -> ActionRollResult`
- **Inputs:**
  - `stat`: Primary character stat, expected around 1–3 but not explicitly clamped.
  - `adds`: Flat modifier (positive or negative) added to the action score.
- **Behavior:** Rolls `d6` for the action die and two independent `d10` challenge dice using `random.randint`, which inherently constrains die faces to their ranges. Computes `action_score = action_die + stat + adds` and determines outcome (Strong/Weak Hit or Miss) by comparing the score to both challenge dice. Identifies a "match" when the challenge dice are equal but does not alter the outcome based on doubles. Returns an `ActionRollResult` containing dice values, calculated score, outcome enum, and match flag.
- **Outputs:** `ActionRollResult` dataclass with human-readable `__str__` output formatting the roll details.

### `calculate_probability(stat: int, adds: int = 0) -> dict[str, float]`
- **Inputs:** Same `stat` and `adds` parameters as `action_roll`.
- **Behavior:** Enumerates all 600 combinations of `d6` and two `d10` rolls to tally outcome frequencies given the supplied modifiers. Uses the same comparison rules as `action_roll`; rounding is applied to three decimal places when returning probabilities.
- **Outputs:** Dictionary mapping `"strong_hit"`, `"weak_hit"`, and `"miss"` to floating-point probabilities rounded to thousandths.

### `ProgressTrack.progress_roll() -> ProgressRollResult`
- **Inputs:** Uses the instance's `ticks` and `rank` to derive `progress = boxes` (0–10). No external parameters.
- **Behavior:** Rolls two `d10` challenge dice with `random.randint`. Determines Strong/Weak Hit or Miss by comparing `progress` to both dice, marking a match when the challenge dice are equal. No special handling for double-1 or double-10 beyond the generic match flag.
- **Outputs:** `ProgressRollResult` containing progress value, challenge dice, outcome enum, and match flag with a string formatter.

### `ProgressTrack.mark_progress(times: int = 1) -> int`
- **Inputs:** `times` multiplier for rank-based progress increments.
- **Behavior:** Adds `RANK_PROGRESS[rank] * times` ticks and clamps at the 40-tick track maximum to avoid overflow.
- **Outputs:** Updated tick count.

### `Momentum` methods
- **Inputs/Behavior:**
  - `gain(amount: int = 1)`: Increases momentum but clamps at `max_value`.
  - `lose(amount: int = 1)`: Decreases momentum but clamps at `min_value`.
  - `reset()`: Restores momentum to `reset_value` after burning.
  - `can_burn(challenge_dice)`: Validates whether momentum exceeds at least one challenge die (and is positive).
  - `burn(original_result, challenge_dice)`: If burning improves the outcome tier, resets momentum and returns the improved `RollResult`; otherwise returns `None`.
- **Outputs:** Updated momentum integers or improved roll results as noted.

## Rule Coverage and Edge Cases
- **Criticals/Advantage/Disadvantage:** The engine does not implement explicit critical success/failure states or advantage/disadvantage mechanics. Challenge-dice matches are flagged via `is_match` but do not modify results.
- **RNG Seeding:** Dice use Python's `random.randint` without local seeding; determinism must be controlled externally by setting `random.seed` before invoking these functions.
- **Dice Range Clamping:** Dice ranges are enforced by `randint` bounds. Inputs such as `stat`, `adds`, or `times` are not clamped and may lead to unusually high or negative action scores.
- **Modifier Combination:** Modifiers are additive only (`action_score = d6 + stat + adds`); no multiplicative or advantage-based adjustments occur.
- **Probability Formatting:** `calculate_probability` returns probabilities rounded to three decimal places.
- **Deterministic / Fixed Rolls:** No built-in support for supplying fixed roll values; deterministic behavior relies on external RNG seeding.
- **Special Outcomes:** No bespoke handling for double-1 or double-6 challenge dice beyond the match flag; matches do not override standard outcome comparisons.

## Testing Coverage and Gaps
- No automated tests currently exercise `action_roll`, `calculate_probability`, or momentum/progress roll logic. The test suite seeds RNG in unrelated contexts, but there are no targeted dice-mechanic tests to cover matches, extreme modifiers, invalid inputs, or interactions such as burning momentum after specific roll patterns.

