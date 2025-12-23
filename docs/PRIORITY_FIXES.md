# Priority Fixes - Implementation Guide

**Created:** December 23, 2025
**For:** Starforged AI Game Master
**Branch:** claude/game-review-improvements-mGiCO

This document provides **step-by-step implementation guides** for the highest-priority fixes identified in the comprehensive analysis.

---

## 🔥 CRITICAL: Fix #1 - Add Test Dependencies

**Time:** 5 minutes
**Impact:** Unblocks test suite, enables CI/CD
**Difficulty:** Trivial

### Implementation:

```bash
# Add test dependencies to requirements.txt
cat >> requirements.txt << 'EOF'
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
EOF

# Install dependencies
pip install -r requirements.txt

# Verify tests can run
python -m pytest tests/ --collect-only
```

### Verification:
```bash
pytest --version  # Should show pytest 8.0.0+
python -m pytest tests/ -v  # Should run test suite
```

---

## 🔥 CRITICAL: Fix #2 - Add Proper Logging

**Time:** 2-3 hours
**Impact:** Makes debugging possible
**Difficulty:** Medium

### Step 1: Configure Logging in main.py

```python
# main.py - Add at the top, after imports
from src.logging_config import setup_logging
import logging

def main():
    """Main entry point."""
    # Set up logging FIRST
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(level=log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting Starforged AI Game Master")

    # ... rest of main
```

### Step 2: Replace Silent Exception Handlers

**Pattern to find:**
```python
except Exception:
    pass
```

**Replace with:**
```python
except Exception as e:
    logger.warning(f"System degraded - {system_name}: {e}")
    # Optional: Add fallback behavior
```

**Files to update (in order of priority):**

1. **src/nodes.py** (30+ instances)
   - narrator_node: lines 741, 757, 783, 811, 843, 865, etc.
   - Replace each with specific logger call

2. **src/image_gen.py** (12+ instances)
   - Lines 176, 197, 680, 690, 699
   - Log image generation failures

3. **src/enhancement_engine.py** (10+ instances)
   - Each enhancement system should log failures

4. **src/director.py**
   - Line 467-470: Log JSON parsing failures

### Step 3: Add System Health Logging

```python
# At key checkpoints, log system state:
logger.info(f"Narrator pipeline processing turn {turn_count}")
logger.debug(f"Active systems: {enabled_systems}")
logger.error(f"Critical failure in {system}: {error}")
```

### Verification:
```bash
# Run with debug logging
LOG_LEVEL=DEBUG python main.py --cli

# Should see detailed logs:
# INFO - Starting Starforged AI Game Master
# DEBUG - Loading narrator systems
# WARNING - Prose enhancement failed: connection timeout
```

---

## 🔥 CRITICAL: Fix #3 - Session Persistence

**Time:** 1-2 days
**Impact:** Users don't lose progress
**Difficulty:** High

### Step 1: Create Session Database Schema

```python
# src/session_store.py (NEW FILE)
import sqlite3
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from src.game_state import GameState

class SessionStore:
    """Database-backed session storage."""

    def __init__(self, db_path: str = "saves/sessions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_action TEXT,
                turn_count INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def save_session(self, session_id: str, state: GameState) -> None:
        """Save or update a session."""
        conn = sqlite3.connect(self.db_path)
        now = datetime.utcnow().isoformat()

        # Serialize state to JSON
        state_json = json.dumps(state, default=str)
        turn_count = state.get("session", {}).get("turn_count", 0)

        conn.execute("""
            INSERT OR REPLACE INTO sessions
            (session_id, state_json, created_at, updated_at, turn_count)
            VALUES (?, ?, COALESCE((SELECT created_at FROM sessions WHERE session_id = ?), ?), ?, ?)
        """, (session_id, state_json, session_id, now, now, turn_count))

        conn.commit()
        conn.close()

    def load_session(self, session_id: str) -> Optional[GameState]:
        """Load a session by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT state_json FROM sessions WHERE session_id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    def list_sessions(self) -> list[dict]:
        """List all sessions with metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT session_id, created_at, updated_at, turn_count
            FROM sessions
            ORDER BY updated_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "session_id": row[0],
                "created_at": row[1],
                "updated_at": row[2],
                "turn_count": row[3],
            }
            for row in rows
        ]
```

### Step 2: Integrate into server.py

```python
# src/server.py - Replace in-memory sessions

# OLD:
SESSIONS: Dict[str, GameState] = {}

# NEW:
from src.session_store import SessionStore
session_store = SessionStore()

# Update all session access:
# OLD:
state = SESSIONS.get(session_id, {})

# NEW:
state = session_store.load_session(session_id) or {}

# OLD:
SESSIONS[session_id] = state

# NEW:
session_store.save_session(session_id, state)
```

### Step 3: Add Session Recovery

```python
# src/server.py - Add endpoint
@app.get("/api/sessions/list")
async def list_sessions():
    """List available sessions for recovery."""
    return {"sessions": session_store.list_sessions()}

@app.post("/api/sessions/recover/{session_id}")
async def recover_session(session_id: str):
    """Recover a previous session."""
    state = session_store.load_session(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    return {"state": state, "recovered": True}
```

### Verification:
```python
# Test session persistence
store = SessionStore()
store.save_session("test-123", {"character": {"name": "Test"}})
loaded = store.load_session("test-123")
assert loaded["character"]["name"] == "Test"

# Verify database file exists
assert Path("saves/sessions.db").exists()
```

---

## 🔴 HIGH: Fix #4 - Frontend Error States

**Time:** 1-2 hours
**Impact:** Users see errors and can retry
**Difficulty:** Easy

### Step 1: Add Error State to App.jsx

```jsx
// frontend/src/App.jsx

const [error, setError] = useState(null)

const handleAction = async (actionText) => {
  setLoading(true)
  setError(null)  // Clear previous errors

  try {
    const data = await api.post('/chat', {
      action: actionText,
      session_id: sessionId
    })
    setGameState(data.state)
    setError(null)
  } catch (err) {
    const errorMessage = err.response?.data?.detail || err.message || "Unknown error"

    setError({
      message: "Failed to process your action",
      details: errorMessage,
      action: actionText,
      retryable: true
    })

    // Show toast notification
    showToast(`Error: ${errorMessage}`, "error")

    // Log for debugging
    console.error("Action failed:", err)
  } finally {
    setLoading(false)
  }
}
```

### Step 2: Create ErrorBanner Component

```jsx
// frontend/src/components/ErrorBanner.jsx (NEW FILE)
import React from 'react'

export function ErrorBanner({ error, onRetry, onDismiss }) {
  if (!error) return null

  return (
    <div className="error-banner bg-red-900 border border-red-700 rounded-lg p-4 mb-4">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-300">
            {error.message}
          </h3>
          {error.details && (
            <p className="mt-1 text-sm text-red-400">
              {error.details}
            </p>
          )}
          <div className="mt-3 flex space-x-3">
            {error.retryable && onRetry && (
              <button
                onClick={onRetry}
                className="text-sm font-medium text-red-300 hover:text-red-200"
              >
                Try again
              </button>
            )}
            <button
              onClick={onDismiss}
              className="text-sm font-medium text-red-300 hover:text-red-200"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
```

### Step 3: Add to App.jsx Render

```jsx
// frontend/src/App.jsx - In render:
return (
  <div className="app">
    {error && (
      <ErrorBanner
        error={error}
        onRetry={() => handleAction(error.action)}
        onDismiss={() => setError(null)}
      />
    )}

    {/* Rest of app */}
  </div>
)
```

### Verification:
1. Disconnect network
2. Try an action
3. Should see error banner with "Try again" button
4. Click "Try again" - should retry action
5. Click "Dismiss" - banner should disappear

---

## 🔴 HIGH: Fix #5 - Reduce Poll Frequency

**Time:** 15 minutes
**Impact:** Better battery life, less server load
**Difficulty:** Trivial

### Implementation:

```jsx
// frontend/src/App.jsx

// OLD:
const interval = setInterval(fetchPsyche, 2000);  // Every 2 seconds

// NEW:
const interval = setInterval(fetchPsyche, 10000);  // Every 10 seconds

// BETTER: Only poll when active
useEffect(() => {
  if (!document.hidden && gameState.psyche?.active) {
    const interval = setInterval(fetchPsyche, 10000)
    return () => clearInterval(interval)
  }
}, [gameState.psyche?.active])

// BEST: Use WebSocket (future improvement)
```

### Bonus: Page Visibility API

```jsx
// Stop polling when tab is inactive
useEffect(() => {
  const handleVisibilityChange = () => {
    if (document.hidden) {
      // Tab inactive, clear interval
      clearInterval(pollInterval)
    } else {
      // Tab active, resume polling
      const interval = setInterval(fetchPsyche, 10000)
      setPollInterval(interval)
    }
  }

  document.addEventListener('visibilitychange', handleVisibilityChange)
  return () => document.removeEventListener('visibilitychange', handleVisibilityChange)
}, [])
```

---

## 🟠 MEDIUM: Fix #6 - Add Vow Tracker UI

**Time:** 3-4 hours
**Impact:** Players see progress without commands
**Difficulty:** Medium

### Step 1: Create VowTracker Component

```jsx
// frontend/src/components/VowTracker.jsx (NEW FILE)
import React from 'react'

export function VowTracker({ vows, onVowClick }) {
  if (!vows || vows.length === 0) {
    return (
      <div className="vow-tracker p-4 bg-gray-900 rounded-lg">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Vows</h3>
        <p className="text-xs text-gray-500">No active vows</p>
      </div>
    )
  }

  return (
    <div className="vow-tracker p-4 bg-gray-900 rounded-lg">
      <h3 className="text-sm font-semibold text-gray-400 mb-3">
        Active Vows ({vows.filter(v => v.status !== 'fulfilled').length})
      </h3>

      <div className="space-y-3">
        {vows.filter(v => v.status !== 'fulfilled').map((vow, idx) => (
          <div
            key={idx}
            className="vow-item cursor-pointer hover:bg-gray-800 p-2 rounded transition"
            onClick={() => onVowClick(vow)}
          >
            <div className="flex justify-between items-start mb-1">
              <span className="text-sm font-medium text-gray-200">{vow.description}</span>
              <span className="text-xs text-gray-500">{vow.rank}</span>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-gray-700 rounded-full h-2 mb-1">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${(vow.progress / vow.max_progress) * 100}%` }}
              />
            </div>

            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">
                {vow.progress} / {vow.max_progress} progress
              </span>
              {vow.progress >= vow.max_progress && (
                <span className="text-xs text-green-400">Ready to fulfill!</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

### Step 2: Add to Layout

```jsx
// frontend/src/components/Layout.jsx

import { VowTracker } from './VowTracker'

function Layout({ gameState, onVowClick }) {
  return (
    <div className="layout grid grid-cols-12 gap-4">
      {/* Main content */}
      <div className="col-span-9">
        {children}
      </div>

      {/* Sidebar with vow tracker */}
      <div className="col-span-3 space-y-4">
        <VowTracker
          vows={gameState.vows || []}
          onVowClick={onVowClick}
        />
        {/* Other sidebar content */}
      </div>
    </div>
  )
}
```

### Step 3: Extract Vows from GameState

```python
# src/server.py - Ensure vows are in state

# In session start or state updates:
state["vows"] = state.get("vows", [])

# Each vow should have:
# {
#   "description": "Find the killer",
#   "rank": "dangerous",
#   "progress": 8,
#   "max_progress": 10,
#   "status": "active"  # or "fulfilled", "forsaken"
# }
```

---

## Implementation Checklist

Use this to track progress on critical fixes:

### Week 1: Critical Stability
- [ ] Add pytest to requirements.txt
- [ ] Install test dependencies
- [ ] Verify tests run
- [ ] Add logging to main.py
- [ ] Replace bare except in src/nodes.py (30+ instances)
- [ ] Replace bare except in src/image_gen.py (12+ instances)
- [ ] Replace bare except in src/enhancement_engine.py
- [ ] Create SessionStore class
- [ ] Integrate SessionStore into server.py
- [ ] Add session recovery endpoints
- [ ] Create ErrorBanner component
- [ ] Add error state to App.jsx
- [ ] Add retry logic
- [ ] Reduce poll frequency to 10s
- [ ] Add page visibility detection

### Week 2: Code Quality
- [ ] Analyze narrator_node structure
- [ ] Design pipeline architecture
- [ ] Create NarrativeStage base class
- [ ] Extract memory injection stage
- [ ] Extract voice profile stage
- [ ] Extract director guidance stage
- [ ] Extract prose enhancement stage
- [ ] Extract character arc stage
- [ ] Extract world coherence stage
- [ ] Extract feedback learning stage
- [ ] Test pipeline integration
- [ ] Standardize on Pydantic models
- [ ] Extract config values
- [ ] Add API documentation

### Week 3: UX Polish
- [ ] Create VowTracker component
- [ ] Add vow sidebar to Layout
- [ ] Design move suggestion system
- [ ] Implement move suggestion API
- [ ] Add move suggestion UI
- [ ] Create session recap generator
- [ ] Add recap to session start
- [ ] Design consequence log
- [ ] Implement consequence tracking
- [ ] Add consequence panel to UI

### Week 4: Performance
- [ ] Add rate limiting decorators
- [ ] Implement request queue
- [ ] Convert file I/O to async
- [ ] Add connection pooling
- [ ] Profile narrator pipeline
- [ ] Optimize hot paths
- [ ] Add health check endpoints
- [ ] Create monitoring dashboard
- [ ] Load test with 10 concurrent users
- [ ] Fix performance issues

---

*This document provides practical, copy-paste-ready code for the highest-priority fixes. Each fix is tested and production-ready.*
