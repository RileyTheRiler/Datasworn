# Dice Probability Helpers

This guide documents the dice utilities that back the roll odds UI and automated narration hooks. Function names and parameters below match the implementations in `src/rules_engine.py` so you can copy/paste them directly.

## Quick call reference
- **Ironsworn action roll**
  ```python
  from src.rules_engine import action_roll

  result = action_roll(stat=2, adds=1)
  ```
- **Ironsworn odds preview**
  ```python
  from src.rules_engine import calculate_probability

  odds = calculate_probability(stat=2, adds=1)
  ```
- **PbtA 2d6 roll odds**
  ```python
  from src.rules_engine import calculate_2d6_probability

  pbta_odds = calculate_2d6_probability(modifier=1)
  ```
- **d20 DC check odds (with advantage/disadvantage support)**
  ```python
  from src.rules_engine import calculate_d20_probability

  dc_odds = calculate_d20_probability(dc=15, modifier=3, advantage=True)
  ```

## Worked probability examples

### 2d6 + modifier (PbtA style)
`calculate_2d6_probability(modifier=1)` iterates all 36 combinations of two d6s, adds the modifier, and buckets results into 10+ strong hits, 7-9 weak hits, and 6- misses. The helper returns:

```
{'strong_hit': 0.278, 'weak_hit': 0.444, 'miss': 0.278}
```

That means a +1 modifier yields a 27.8% strong hit rate (10 of 36 outcomes), 44.4% weak hits (16 of 36), and 27.8% misses (10 of 36).

### d20 ability checks with advantage/disadvantage
`calculate_d20_probability(dc=15, modifier=3, advantage=True)` enumerates all 400 ordered roll pairs, keeps the higher die for advantage, and measures how many totals meet or exceed the DC. It also tracks natural 20 and natural 1 frequencies. The output is:

```
{'success': 0.698, 'failure': 0.302, 'critical_success': 0.098, 'critical_failure': 0.003}
```

Switching to disadvantage with the same DC and modifier flips the curve, using the lower die in each of the 400 pairs:

```
{'success': 0.203, 'failure': 0.797, 'critical_success': 0.003, 'critical_failure': 0.098}
```

Because the helper enumerates every possible outcome instead of sampling, these values exactly match what you will see in automated outputs.

## Behavioral guarantees and assumptions
- **Random seeding**: Probability helpers use exhaustive enumeration and ignore random seeds. The `action_roll` function uses Python's `random` module; seed it externally (e.g., `random.seed(42)`) when you need reproducible single-roll results.
- **Critical bands**: `calculate_d20_probability` always reports the natural 20 band as `critical_success` and natural 1 band as `critical_failure`, regardless of whether the roll also meets the DC threshold.
- **Fixed rolls with advantage/disadvantage**: When you pass `fixed_roll`, the helper ignores advantage/disadvantage flags and treats that number as the resolved die face, ensuring deterministic previews that still honor critical-band reporting.
- **Percentage formatting**: All helpers return rounded decimal probabilities (three decimal places). Multiply by 100 when you want percentage strings; e.g., `0.698` → `69.8%`.
