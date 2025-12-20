# Psychological Systems - GM Guide

## Overview

The psychological system creates a dynamic, evolving mental landscape for characters. As GM, you can leverage these mechanics to create deeply personal, emotionally resonant stories.

---

## Core Philosophy

**Psychology is not a punishment system**—it's a narrative engine. Trauma creates opportunities for growth, coping creates character moments, and healing creates arcs.

---

## Triggering Psychological Events

### Stress Increases
Award stress when:
- Player fails a critical move
- Character witnesses something horrific
- Relationships are damaged
- Resources are lost
- Time pressure mounts

**Recommended**: +10-20% per significant event

### Sanity Decreases
Reduce sanity when:
- Character encounters cosmic horror
- Reality is questioned (hallucinations, paradoxes)
- Trauma scars are triggered
- Character uses mind-altering substances

**Recommended**: -5-15% per event

### Emotional Shifts
Change emotion when:
- Major narrative beats occur
- Relationships change dramatically
- Character makes difficult choices

---

## Using Personalized Mysteries

### How It Works
The system analyzes the character's trauma scars and dominant traits to generate mysteries that target their specific fears.

### Fear Categories

| Fear | Trauma/Trait | Mystery Type |
|---|---|---|
| **Betrayal** | Shattered Trust | Trusted ally is the threat |
| **Infiltration** | Paranoia | Shapeshifter/spy among crew |
| **Environmental Threat** | Jittery Nerves | Sabotage, life support failure |
| **Loss of Control** | Cold Logic | Mind control, manipulation |
| **Harm to Loved Ones** | High Empathy | Blackmail, hostage situation |

### When to Use
- Start of new arc
- After character acquires trauma
- When player seems disengaged (personalization re-engages)

### API Call
```
GET /api/mystery/personalized/{session_id}
```

---

## Roleplay

ing NPC Emotional Memory

### How It Works
NPCs store the last 5 emotional interactions with the player. They remember panic attacks, outbursts, confessions, etc.

### How to Use in Dialogue

**Bad**:
> "How are you doing?"

**Good**:
> "Last time we talked, you were terrified. The panic attack in the med bay... are you okay now?"

### Building Trust
NPCs who witness vulnerability can become allies. Use emotional memory to:
- Offer support
- Create bonding moments
- Unlock new dialogue options

---

## Balancing Difficulty Scaling

### The Formula
```
difficulty = base + (trauma_count × 0.1) + (1.0 - sanity) × 0.2 + addiction × 0.2
```

### What This Means
- 3 traumas + 50% sanity = +40% harder
- This affects ALL skill checks globally

### When to Adjust
If difficulty becomes punishing:
1. Offer therapy opportunities
2. Provide coping mechanism access
3. Create "safe" scenes for recovery

---

## Therapy Sessions

### Structure
1. **Opening**: "How are you holding up?"
2. **Exploration**: Discuss the trauma scar
3. **Progress**: Increment therapy counter
4. **Outcome**: Check for arc evolution

### Pacing
- 1 session per in-game week (recommended)
- Don't rush—healing takes time
- Celebrate milestones (10, 20, 30 sessions)

### Dialogue Tips
- Be empathetic, not clinical
- Reference specific events from the character's history
- Acknowledge progress, even if small

---

## Managing Addiction

### Warning Signs
- Player uses stims 3+ times
- Addiction level > 0.5

### Roleplay Opportunities
- Withdrawal symptoms during tense moments
- NPCs express concern
- Offer "one last hit" temptations
- Create recovery arcs

### Mechanical Effects
- -1 to all rolls when not using (addiction ≥ 0.5)
- -2 penalty at severe addiction (≥ 0.8)

---

## Permadeath

### Triggers
1. Sanity = 0%
2. 5+ fresh (unintegrated) trauma scars

### How to Handle
**This is a feature, not a bug.** Permadeath creates stakes.

**When it happens**:
1. Narrate the final moment with gravitas
2. Describe the psychotic break or mental collapse
3. Offer the player a chance to create a new character
4. Consider: Does the lost character become an NPC antagonist?

### Preventing It
- Warn players at 20% sanity
- Offer therapy after 3 traumas
- Create "intervention" scenes where NPCs notice

---

## Audio-Visual Immersion

### Sound Cues (Automatic)
- **Stress > 70%**: Heartbeat loop
- **Sanity < 30%**: Whispers
- **Sanity < 15%**: Static interference

### Visual Effects (Automatic)
- **Sanity < 30%**: Chromatic aberration (red/cyan split)
- **Trauma Scars**: Vignette darkening
- **Emotion = Afraid**: Screen shake

### Narration Tips
When these effects trigger, describe them in-fiction:
- "Your heart pounds in your ears."
- "You hear whispers in the vents. Are they real?"
- "The lights seem to split into red and blue halos."

---

## Example Session Flow

### Act 1: Stress Buildup
- Mission goes wrong
- Stress increases to 85%
- Player uses Meditate (success)
- Stress drops to 65%

### Act 2: Breaking Point
- Critical failure on key move
- Stress hits 92%
- Breaking point triggered
- "Shattered Trust" trauma acquired
- Stress resets to 40%, sanity drops to 70%

### Act 3: Personalized Mystery
- Generate mystery based on "Shattered Trust"
- Medic is revealed as the threat
- Player must confront their fear of betrayal

### Act 4: Therapy Arc
- 10 sessions with Dr. Chen
- "Shattered Trust" evolves to "Cautious Trust"
- Player learns to trust again, slowly

---

## API Reference

| Endpoint | Purpose |
|---|---|
| `POST /api/psyche/coping` | Apply coping mechanism |
| `POST /api/psyche/therapy` | Complete therapy session |
| `GET /api/psyche/available-coping/{id}` | Get available mechanisms |
| `POST /api/psyche/check-breaking-point/{id}` | Check for trauma |
| `GET /api/mystery/personalized/{id}` | Generate personalized mystery |
| `GET /api/difficulty/modifier/{id}` | Get difficulty modifier |

---

## Final Advice

**Trust the system.** The psychological mechanics are designed to create emergent stories. Let trauma happen, let players struggle, and let healing be earned. The best stories come from characters who break and rebuild themselves.
