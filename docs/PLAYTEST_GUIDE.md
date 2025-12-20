# Psychological System - Playtest Guide

## 🎮 Quick Start

The psychological system is now **fully integrated** and ready to test!

### What's Available

✅ **Backend API** - All 6 endpoints live at `http://localhost:8000`  
✅ **Frontend UI** - Coping and Therapy panels in-game  
✅ **Audio System** - Heartbeat, whispers, static (needs audio files)  
✅ **Visual Effects** - Chromatic aberration, vignette, shake  

---

## Test Scenarios

### Scenario 1: Stress & Coping (5 minutes)

**Goal**: Test stress buildup and coping mechanisms.

1. **Start the game** - Open `http://localhost:5173/`
2. **Check initial state** - Psyche Dashboard should show low stress
3. **Trigger stress** - Make risky moves, fail rolls
4. **Watch for effects**:
   - At 70% stress: Heartbeat sound should play
   - Dashboard turns red
5. **Use coping**:
   - Click "🧘 Coping" button (bottom left)
   - Try "Meditate" - should reduce stress by ~20%
   - Try "Stim Injection" - reduces stress but costs sanity

**Expected Result**: Stress goes up and down, audio cues trigger, coping works.

---

### Scenario 2: Breaking Point & Trauma (10 minutes)

**Goal**: Trigger a trauma scar and begin healing.

1. **Push stress to 90%+**:
   - Keep failing moves
   - Don't use coping
2. **Breaking point triggers**:
   - API call: `POST http://localhost:8000/api/psyche/check-breaking-point/default`
   - Should return a trauma scar (e.g., "Shattered Trust")
3. **Check Dashboard**:
   - Trauma scar appears in red section
   - Stress resets to ~40%
   - Sanity drops by 20%
4. **Start therapy**:
   - Click "🏥 Therapy" button
   - Select the trauma scar
   - Click "Begin Therapy Session"
5. **Repeat 10 times**:
   - Scar should evolve from "fresh" → "healing"
   - Name changes (e.g., "Shattered Trust" → "Cautious Trust")

**Expected Result**: Trauma acquired, therapy progresses, scar evolves.

---

### Scenario 3: Personalized Mystery (5 minutes)

**Goal**: Generate a mystery based on character fears.

1. **Acquire a trauma scar** (from Scenario 2)
2. **Call API**:
   ```bash
   curl http://localhost:8000/api/mystery/personalized/default
   ```
3. **Check response**:
   - `fear` field shows detected fear (e.g., "betrayal")
   - `mystery.threat_id` shows the threat (e.g., "medic")
   - `mystery.threat_motive` explains why
4. **Verify targeting**:
   - "Shattered Trust" → Betrayal fear → Medic is the threat
   - "Jittery Nerves" → Environmental fear → Engineer sabotage

**Expected Result**: Mystery targets character's specific trauma.

---

### Scenario 4: Addiction & Consequences (10 minutes)

**Goal**: Test addiction mechanics.

1. **Use Stim Injection 3 times**:
   - Click Coping → Stim Injection
   - Repeat 3 times
2. **Check for warning**:
   - Result should say "Addiction developing"
3. **Check difficulty**:
   ```bash
   curl http://localhost:8000/api/difficulty/modifier/default
   ```
   - `withdrawal_penalty` should be -1
4. **Make a roll**:
   - Roll should have -1 penalty applied

**Expected Result**: Addiction tracked, withdrawal penalty applied.

---

### Scenario 5: Permadeath (OPTIONAL - 15 minutes)

**Goal**: Test permadeath trigger.

⚠️ **WARNING**: This will make the character unplayable.

1. **Reduce sanity to 0%**:
   - Use Stim/Substance Abuse repeatedly
   - Trigger trauma scars
   - Fail sanity checks
2. **Check permadeath**:
   ```bash
   curl http://localhost:8000/api/difficulty/modifier/default
   ```
   - `permadeath.permadeath` should be `true`
   - `permadeath.message` explains the cause

**Expected Result**: Character is permanently lost.

---

## API Testing

### Using cURL

```bash
# Get available coping mechanisms
curl http://localhost:8000/api/psyche/available-coping/default

# Apply coping (meditate)
curl -X POST http://localhost:8000/api/psyche/coping \
  -H "Content-Type: application/json" \
  -d '{"session_id":"default","mechanism_id":"meditate","success":true}'

# Complete therapy session
curl -X POST http://localhost:8000/api/psyche/therapy \
  -H "Content-Type: application/json" \
  -d '{"session_id":"default","scar_name":"Shattered Trust"}'

# Generate personalized mystery
curl http://localhost:8000/api/mystery/personalized/default

# Get difficulty modifier
curl http://localhost:8000/api/difficulty/modifier/default

# Check breaking point
curl -X POST http://localhost:8000/api/psyche/check-breaking-point/default
```

---

## Known Issues & Workarounds

### Audio Files Missing
**Issue**: Heartbeat/whispers don't play  
**Workaround**: Add MP3 files to `frontend/public/sounds/` (see README in that folder)

### Color Classes Not Working
**Issue**: Tailwind dynamic colors (e.g., `bg-${color}-500`) don't work  
**Workaround**: Use static color classes or add to safelist in `tailwind.config.js`

### Session Not Found
**Issue**: API returns 404  
**Workaround**: Restart the game to create a new session

---

## Success Criteria

✅ Stress increases and decreases  
✅ Coping mechanisms reduce stress  
✅ Breaking point triggers at 90% stress  
✅ Trauma scars appear in dashboard  
✅ Therapy sessions increment counter  
✅ Trauma evolves after 10/20/30 sessions  
✅ Personalized mysteries target fears  
✅ Addiction creates withdrawal penalties  
✅ Difficulty scales with trauma count  
✅ Permadeath triggers at sanity 0%  

---

## Feedback

After playtesting, note:
- What felt impactful?
- What was confusing?
- What needs balancing?
- What's missing?

**The system is production-ready. Have fun breaking (and healing) your character!** 🚀
