# Gameplay Improvement Recommendations

This guide focuses on tightening session flow and making each move feel more meaningful for players interacting with the Starforged AI Game Master.

> **Implementation Status**: Items marked with ✅ are implemented, 🔧 are in progress, ⏳ are planned.

---

## 1) Smooth onboarding and clarity
- ⏳ **Guided first session**: Provide a short, optional setup wizard that walks through entering character info, first vow, and starting location before showing the main prompt.
- ⏳ **Contextual shortcuts**: Surface the most useful keyboard shortcuts (R for rolls, F5/F9 for save/load) in a persistent help strip and surface the `!status`/`!vows` commands in early prompts.
- ⏳ **Example-led prompts**: Seed the opening prompt area with 2–3 clickable example intents (scout, diplomat, investigator) to model strong player inputs.

---

## 2) Keep consequences visible ✅
- ✅ **Fail-forward defaults**: Encourage the GM to reply with a cost/complication on Weak Hits and clear consequences on Misses instead of dead ends.
  - *Implemented in `consequence_tracker.py` with `generate_consequence_from_roll()`*
- ✅ **Consequence log**: Add a small panel (or `!consequences` command) that lists recent complications, debts, injuries, and clock progress so players remember to act on them.
  - *Implemented in `consequence_tracker.py` with full CRUD API endpoints*
  - *API: `GET /api/ux/consequences/{session_id}`*
- ✅ **Escalation hints**: When tension is high, propose 1–2 next actions that resolve or embrace the risk (patch the leak, flee, negotiate) rather than letting the player stall.
  - *Auto-escalation implemented in `ConsequenceTracker.advance_turn()`*

---

## 3) Highlight vows and progress ✅
- ✅ **Visible vow tracker**: Keep active vows visible during play (sidebar or periodic text reminders) so choices stay connected to goals.
  - *Implemented in `vow_tracker.py` with progress bars and phase detection*
  - *API: `GET /api/ux/vows/{session_id}`*
- ✅ **Progress-aware guidance**: When a vow nears completion, prompt for a climax setup (gather allies, confront foe) and suggest fitting moves.
  - *Phase detection: "establishing", "developing", "approaching_climax", "ready_to_fulfill"*
  - *Each phase includes suggested actions and dramatic tension text*
- ✅ **Quick recap**: Offer a one-line recap after major scenes summarizing vow progress, NPC mood shifts, and outstanding threads.
  - *Implemented in `session_continuity.py` with `generate_session_recap()`*

---

## 4) Teach the move set in play ✅
- ✅ **Move suggestions**: When players describe intent without naming a move, propose the top 2–3 candidate moves with the linked stat ("This sounds like Edge: Secure an Advantage").
  - *Implemented in `move_suggester.py` with keyword matching and confidence scoring*
  - *API: `POST /api/ux/moves/suggest`*
- ⏳ **Oracle transparency**: After rolling, briefly cite which oracle or table influenced the result to build trust and teach the system.
- ✅ **Cheat-sheet access**: Provide a lightweight move reference (inline modal or `!moves`) so players can confirm outcomes without leaving the flow.
  - *API: `GET /api/ux/moves/list` and `GET /api/ux/moves/help/{move_name}`*

---

## 5) Pacing and scene structure 🔧
- 🔧 **Scene beats**: Nudge the GM to keep scenes under ~3 exchanges before changing location, escalating, or revealing new info.
  - *Director system tracks `scenes_since_breather`*
- ✅ **Downbeat interludes**: After intense scenes, suggest recovery actions (Forge a Bond, Make Camp analogues) to stabilize pacing and spotlight relationships.
  - *Quiet moment detection in director_node*
- ✅ **Cliffhanger exits**: Encourage ending sessions with a cliffhanger plus a save reminder to make re-entry easier.
  - *Implemented in `session_continuity.py` with `generate_cliffhanger()`*
  - *API: `GET /api/ux/session/{session_id}/end`*

---

## 6) Reusable templates and exports 🔧
- ✅ **Scenario jumpstarts**: Ship 2–3 curated starting situations (derelict salvage, blockade diplomacy, shipboard mystery) that pre-load truths, threats, and NPCs.
  - *Ship campaign template exists in `ship_campaign_template.py`*
- ✅ **Session exports**: Keep the existing export log prominent and add a "session highlights" summary (major rolls, vow changes, notable NPC beats) for sharing.
  - *Session summary with highlights in `session_continuity.py`*
  - *`format_session_end_screen()` provides formatted output*
- ⏳ **Feedback hooks**: After export, ask for quick thumbs-up/down on pacing, tone, and move clarity to feed the feedback-learning engine.

---

## 7) Accessibility and UX polish 🔧
- ⏳ **Readable defaults**: Favor high-contrast themes and adjustable text size in both CLI and web modes.
- ✅ **Input resilience**: Autosave before rolls and after scene transitions; recover from accidental reloads gracefully.
  - *AutoSaveSystem exists and is integrated*
- ⏳ **Multimodal cues**: When voice is enabled, display captions and a transcript toggle so no one misses results.

---

## Implementation Summary

| Category | Status | Key Files |
|----------|--------|-----------|
| Consequence Tracking | ✅ Complete | `consequence_tracker.py`, `ux_api.py` |
| Vow Visibility | ✅ Complete | `vow_tracker.py`, `ux_api.py` |
| Move Suggestions | ✅ Complete | `move_suggester.py`, `ux_api.py` |
| Session Continuity | ✅ Complete | `session_continuity.py`, `ux_api.py` |
| Pacing/Scene Structure | 🔧 Partial | `director.py`, `nodes.py` |
| Onboarding | ⏳ Planned | - |
| Accessibility | 🔧 Partial | `auto_save.py` |

### API Endpoints Added

All new endpoints are under `/api/ux/`:

```
Vows:
  GET  /vows/{session_id}
  POST /vows/calculate-progress

Consequences:
  GET  /consequences/{session_id}
  POST /consequences/{session_id}/add
  POST /consequences/{session_id}/resolve
  POST /consequences/{session_id}/advance-turn
  POST /consequences/suggest

Moves:
  POST /moves/suggest
  GET  /moves/help/{move_name}
  GET  /moves/list

Session:
  GET  /session/{session_id}/recap
  POST /session/{session_id}/event
  GET  /session/{session_id}/end
  POST /session/{session_id}/record-roll
  POST /session/{session_id}/record-npc
  POST /session/{session_id}/record-location

Dashboard:
  GET  /dashboard/{session_id}
```
