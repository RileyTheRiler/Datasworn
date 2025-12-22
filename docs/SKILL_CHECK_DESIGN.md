# Skill Check Design Playbook

This playbook translates the best parts of **Disco Elysium** (2d6 bell curve) and **Baldur's Gate 3** (d20 with advantage) into actionable guidance for the Starforged AI Game Master. Use it when designing new moves, narrative gates, or UI feedback.

## Principles

- **Probability you can feel:** Use bell curves for reliability (Disco) and flat curves for swingy, high‑tension moments (BG3). Communicate the odds before a roll.
- **Fail forward:** Every miss should produce story, not just a "try again later" message. Script bespoke failure beats for key checks.
- **Transparent modifiers:** Show how clothing/gear, status effects, narrative clues, or companions adjust the roll. This builds trust and invites experimentation.
- **Second chances with cost:** Retries should require investment—spend a resource, learn new information, or accept a consequence.

## Mechanical Templates

### Disco Elysium style (2d6 bell curve)

- **Formula:** `2d6 + skill + modifiers ≥ difficulty`.
- **Criticals:** Double 6 = auto‑success; Double 1 = auto‑fail (2.78% each).
- **When to use:** Conversational gambits, investigative leaps, and any moment where incremental expertise should noticeably change the odds.
- **Passive vs. active:** For passive gates, treat the roll as a flat 6 instead of rolling dice to reward raw skill investment.

### Baldur's Gate 3 style (d20 with advantage/disadvantage)

- **Formula:** `d20 + modifier ≥ DC` with natural 20 auto‑success and natural 1 auto‑fail.
- **Advantage/disadvantage:** Roll 2d20 take the best/worst for big probability swings (~±3.3 effective modifier).
- **When to use:** High drama or high stakes where luck should matter as much as preparation—social showdowns, desperate stealth, or chaotic combat interactions.
- **Buff windows:** Allow pre‑roll buffs (Guidance‑style cantrips, gear swaps, helpful allies) to encourage party collaboration.

## Implementation hooks

- **Code helpers:** `src/skill_checks.py` implements both systems:
  - `roll_disco_check` and `disco_success_probability` for bell‑curve checks with critical overrides.
  - `roll_baldurs_gate_check` and `baldurs_gate_success_probability` for d20 checks, including advantage/disadvantage.
- **UI feedback:** Surface the probability helpers in chat/CLI before a roll and include a breakdown of modifiers used.
- **Encounter design:** Pair red/white retry logic with Starforged moves—e.g., red = one shot with narrative fallout; white = retry after spending momentum or learning a clue.

## Tuning checklist

- Pick bell curve vs. flat curve based on desired tension profile.
- Set explicit difficulty tiers (Trivial→Heroic) and map them to narrative stakes.
- Decide whether criticals bypass math; if yes, script bespoke outcomes for both extremes.
- Ensure every failure unlocks information, a new complication, or a resource trade.
- Log the modifier breakdown so players can reverse‑engineer why they succeeded or failed.
