# AI Tuning and Director Hooks

This guide exposes the knobs designers can adjust without diving into the full simulation stack.

## Perception and Confidence Controls
- **PerceptionConfig** (in `src/ai_tuning.py`)
  - `sight_range_meters`, `hearing_range_meters`, `peripheral_awareness`, and `evidence_persistence_minutes` give you hard values to pass into stealth/awareness systems.
  - Call `to_context()` to produce a safe dictionary blob that utility AI, behavior trees, or the Director can merge into their state without extra parsing.
- **ConfidenceThresholds**
  - Centralizes the minimum confidence needed for the AI to accept environmental facts, act on a goal, warn the party, or escalate security.
  - Use `gate(confidence, action)` before committing to expensive moves or before surfacing information to the player.

## Hallucination Guardrails
- **HallucinationPolicy**
  - Tunables: `min_sanity`, `reject_below_confidence`, `max_per_scene`, `require_director_approval`.
  - Passed into `PsychologicalEngine.generate_hallucination(...)` to block low-confidence or excessive hallucinations.
  - Supports a `director_approved=True` flag so scripted beats can deliberately allow a hallucination even when the character is unstable.

## Personality Presets
Designer-friendly bundles live in `DESIGNER_PRESETS`:
- **Stealthy Guard** – cautious lookout with high pattern-matching weight.
- **Friendly Merchant** – extroverted trader who prioritizes empathy and relationships.
- **Anxious Survivor** – skittish loner who hoards resources and looks for escape routes.

Use `DesignerProfile.as_prompt()` to inject a concise description plus reasoning weights into prompts or tuning files.

## Quest/Director Injection Hooks
- When a quest script or AI director needs to push goals or facts, convert them into structured beats instead of raw prose.
  - Add short strings to `DirectorPlan.beats` (e.g., `"Secure the relay before dawn"`).
  - Pass contextual facts through `PerceptionConfig.to_context()` and any custom quest metadata so downstream systems receive normalized keys (`perception.sight`, `perception.hearing`).
- Gate risky escalations with `ConfidenceThresholds.gate(..., action="pursue_goal")` before you enqueue new objectives.
- When forcing hallucination-flavored beats, call `generate_hallucination(..., policy=HallucinationPolicy(...), director_approved=True)` so narration stays within the configured limits.
- Always keep directorial injections hidden from players—only the Narrator consumes them. Avoid storing raw player-identifying data; prefer stable IDs or tags so prompts stay anonymized.
