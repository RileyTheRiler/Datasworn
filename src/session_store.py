"""
Session Storage System for Starforged AI Game Master.
Provides database-backed session persistence to prevent data loss on server restart.
"""

from __future__ import annotations
import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from src.logging_config import get_logger

logger = get_logger("session_store")


class SessionStore:
    """Database-backed session storage with automatic persistence."""

    def __init__(self, db_path: str = "saves/sessions.db"):
        """
        Initialize the session store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"SessionStore initialized at {self.db_path}")

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_action TEXT,
                    turn_count INTEGER DEFAULT 0,
                    character_name TEXT
                )
            """)
            conn.commit()
            logger.debug("Session database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize session database: {e}")
            raise
        finally:
            conn.close()

    def save_session(self, session_id: str, state: Dict[str, Any]) -> None:
        """
        Save or update a session.

        Args:
            session_id: Unique session identifier
            state: Game state dictionary to save

        Raises:
            ValueError: If state cannot be serialized
            sqlite3.Error: If database operation fails
        """
        conn = sqlite3.connect(self.db_path)
        try:
            now = datetime.utcnow().isoformat()

            # Serialize state to JSON
            try:
                state_json = json.dumps(state, default=str)
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to serialize state for session {session_id}: {e}")
                raise ValueError(f"State serialization failed: {e}") from e

            # Extract metadata
            turn_count = state.get("session", {}).get("turn_count", 0)
            character_name = state.get("character", {}).get("name", "Unknown")
            last_action = state.get("session", {}).get("last_action", None)

            # Insert or update
            conn.execute("""
                INSERT OR REPLACE INTO sessions
                (session_id, state_json, created_at, updated_at, turn_count, character_name, last_action)
                VALUES (
                    ?,
                    ?,
                    COALESCE((SELECT created_at FROM sessions WHERE session_id = ?), ?),
                    ?,
                    ?,
                    ?,
                    ?
                )
            """, (session_id, state_json, session_id, now, now, turn_count, character_name, last_action))

            conn.commit()
            logger.debug(f"Saved session {session_id} (turn {turn_count}, character: {character_name})")

        except sqlite3.Error as e:
            logger.error(f"Database error saving session {session_id}: {e}")
            raise
        finally:
            conn.close()

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a session by ID.

        Args:
            session_id: Session identifier to load

        Returns:
            Game state dictionary if found, None otherwise

        Raises:
            json.JSONDecodeError: If stored state is corrupted
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT state_json FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()

            if row:
                try:
                    state = json.loads(row[0])
                    logger.info(f"Loaded session {session_id}")
                    return state
                except json.JSONDecodeError as e:
                    logger.error(f"Corrupted session data for {session_id}: {e}")
                    raise

            logger.debug(f"Session {session_id} not found")
            return None

        except sqlite3.Error as e:
            logger.error(f"Database error loading session {session_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session to delete

        Returns:
            True if session was deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted session {session_id}")
            else:
                logger.debug(f"Session {session_id} not found for deletion")
            return deleted
        except sqlite3.Error as e:
            logger.error(f"Database error deleting session {session_id}: {e}")
            raise
        finally:
            conn.close()

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions with metadata.

        Returns:
            List of session metadata dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT session_id, created_at, updated_at, turn_count, character_name
                FROM sessions
                ORDER BY updated_at DESC
            """)
            rows = cursor.fetchall()

            sessions = [
                {
                    "session_id": row[0],
                    "created_at": row[1],
                    "updated_at": row[2],
                    "turn_count": row[3],
                    "character_name": row[4],
                }
                for row in rows
            ]

            logger.debug(f"Listed {len(sessions)} sessions")
            return sessions

        except sqlite3.Error as e:
            logger.error(f"Database error listing sessions: {e}")
            raise
        finally:
            conn.close()

    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.

        Args:
            session_id: Session to check

        Returns:
            True if session exists
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT 1 FROM sessions WHERE session_id = ? LIMIT 1",
                (session_id,)
            )
            exists = cursor.fetchone() is not None
            return exists
        except sqlite3.Error as e:
            logger.error(f"Database error checking session {session_id}: {e}")
            raise
        finally:
            conn.close()

    def get_session_count(self) -> int:
        """
        Get total number of sessions.

        Returns:
            Number of stored sessions
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            return count
        except sqlite3.Error as e:
            logger.error(f"Database error counting sessions: {e}")
            raise
        finally:
            conn.close()

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Delete sessions older than specified days.

        Args:
            days: Delete sessions not updated in this many days

        Returns:
            Number of sessions deleted
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff = cutoff.replace(day=cutoff.day - days)
            cutoff_iso = cutoff.isoformat()

            cursor = conn.execute(
                "DELETE FROM sessions WHERE updated_at < ?",
                (cutoff_iso,)
            )
            conn.commit()
            deleted = cursor.rowcount
            logger.info(f"Cleaned up {deleted} sessions older than {days} days")
            return deleted

        except sqlite3.Error as e:
            logger.error(f"Database error during cleanup: {e}")
            raise
        finally:
            conn.close()


# Global session store instance
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """
    Get the global session store instance.

    Returns:
        SessionStore singleton
    """
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store
