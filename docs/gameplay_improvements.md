# Gameplay Improvement Recommendations

This guide focuses on tightening session flow and making each move feel more meaningful for players interacting with the Starforged AI Game Master.

## 1) Smooth onboarding and clarity
- **Guided first session**: Provide a short, optional setup wizard that walks through entering character info, first vow, and starting location before showing the main prompt.
- **Contextual shortcuts**: Surface the most useful keyboard shortcuts (R for rolls, F5/F9 for save/load) in a persistent help strip and surface the `!status`/`!vows` commands in early prompts.
- **Example-led prompts**: Seed the opening prompt area with 2–3 clickable example intents (scout, diplomat, investigator) to model strong player inputs.

## 2) Keep consequences visible
- **Fail-forward defaults**: Encourage the GM to reply with a cost/complication on Weak Hits and clear consequences on Misses instead of dead ends.
- **Consequence log**: Add a small panel (or `!consequences` command) that lists recent complications, debts, injuries, and clock progress so players remember to act on them.
- **Escalation hints**: When tension is high, propose 1–2 next actions that resolve or embrace the risk (patch the leak, flee, negotiate) rather than letting the player stall.

## 3) Highlight vows and progress
- **Visible vow tracker**: Keep active vows visible during play (sidebar or periodic text reminders) so choices stay connected to goals.
- **Progress-aware guidance**: When a vow nears completion, prompt for a climax setup (gather allies, confront foe) and suggest fitting moves.
- **Quick recap**: Offer a one-line recap after major scenes summarizing vow progress, NPC mood shifts, and outstanding threads.

## 4) Teach the move set in play
- **Move suggestions**: When players describe intent without naming a move, propose the top 2–3 candidate moves with the linked stat ("This sounds like Edge: Secure an Advantage").
- **Oracle transparency**: After rolling, briefly cite which oracle or table influenced the result to build trust and teach the system.
- **Cheat-sheet access**: Provide a lightweight move reference (inline modal or `!moves`) so players can confirm outcomes without leaving the flow.

## 5) Pacing and scene structure
- **Scene beats**: Nudge the GM to keep scenes under ~3 exchanges before changing location, escalating, or revealing new info.
- **Downbeat interludes**: After intense scenes, suggest recovery actions (Forge a Bond, Make Camp analogues) to stabilize pacing and spotlight relationships.
- **Cliffhanger exits**: Encourage ending sessions with a cliffhanger plus a save reminder to make re-entry easier.

## 6) Reusable templates and exports
- **Scenario jumpstarts**: Ship 2–3 curated starting situations (derelict salvage, blockade diplomacy, shipboard mystery) that pre-load truths, threats, and NPCs.
- **Session exports**: Keep the existing export log prominent and add a "session highlights" summary (major rolls, vow changes, notable NPC beats) for sharing.
- **Feedback hooks**: After export, ask for quick thumbs-up/down on pacing, tone, and move clarity to feed the feedback-learning engine.

## 7) Accessibility and UX polish
- **Readable defaults**: Favor high-contrast themes and adjustable text size in both CLI and web modes.
- **Input resilience**: Autosave before rolls and after scene transitions; recover from accidental reloads gracefully.
- **Multimodal cues**: When voice is enabled, display captions and a transcript toggle so no one misses results.
