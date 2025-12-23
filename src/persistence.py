"""Persistence layer for character, vow, and asset data.

Provides a small SQLite-backed store with JSON snapshots and schema
versioning so future migrations can run safely.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from src.game_state import Character


CURRENT_SCHEMA_VERSION = 1


class PersistenceLayer:
    """Lightweight persistence for character-focused data."""

    def __init__(self, db_path: Path | str, snapshot_path: Path | str | None = None):
        self.db_path = Path(db_path)
        self.snapshot_path = Path(snapshot_path) if snapshot_path else self.db_path.with_suffix(".json")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    # ------------------------------------------------------------------
    # Schema management
    # ------------------------------------------------------------------
    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS characters (
                    name TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
                """
            )

            version = self._get_schema_version(conn)
            if version is None:
                self._set_schema_version(conn, CURRENT_SCHEMA_VERSION)
            elif version < CURRENT_SCHEMA_VERSION:
                self._migrate(conn, version)

    def _get_schema_version(self, conn: sqlite3.Connection) -> Optional[int]:
        row = conn.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
        return int(row[0]) if row else None

    def _set_schema_version(self, conn: sqlite3.Connection, version: int) -> None:
        conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', ?)",
            (str(version),),
        )

    def _migrate(self, conn: sqlite3.Connection, from_version: int) -> None:
        """Run migrations up to the current schema version."""

        version = from_version
        while version < CURRENT_SCHEMA_VERSION:
            # Future migrations will be placed here.
            version += 1

        self._set_schema_version(conn, version)

    # ------------------------------------------------------------------
    # Character persistence
    # ------------------------------------------------------------------
    def save_character(self, character: Character) -> None:
        data = json.dumps(character.model_dump())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO characters (name, data) VALUES (?, ?)",
                (character.name, data),
            )
        self._write_snapshot()

    def load_character(self, name: str) -> Optional[Character]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT data FROM characters WHERE name=?", (name,)).fetchone()
        if row:
            return Character.model_validate_json(row[0])

        # Fallback to snapshot when database entry is unavailable
        snapshot = self._read_snapshot()
        if snapshot:
            for entry in snapshot.get("characters", []):
                if entry.get("name") == name:
                    return Character.model_validate(entry["data"])
        return None

    def list_characters(self) -> list[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT name FROM characters ORDER BY name").fetchall()
        return [row[0] for row in rows]

    # ------------------------------------------------------------------
    # Snapshot utilities
    # ------------------------------------------------------------------
    def _write_snapshot(self) -> None:
        snapshot = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "characters": [
                {"name": name, "data": char_data}
                for name, char_data in self._iter_character_rows()
            ],
        }
        self.snapshot_path.write_text(json.dumps(snapshot, indent=2))

    def _iter_character_rows(self) -> Iterable[tuple[str, dict]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT name, data FROM characters").fetchall()
        for name, data in rows:
            yield name, json.loads(data)

    def _read_snapshot(self) -> dict | None:
        if not self.snapshot_path.exists():
            return None
        try:
            return json.loads(self.snapshot_path.read_text())
        except json.JSONDecodeError:
            return None

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------
    @staticmethod
    def export_character_to_file(character: Character, path: Path) -> None:
        payload = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "character": character.model_dump(),
        }
        path.write_text(json.dumps(payload, indent=2))

    @staticmethod
    def parse_character_payload(data: dict) -> Character:
        if "character" in data:
            return Character.model_validate(data["character"])
        if "data" in data and isinstance(data["data"], dict):
            return Character.model_validate(data["data"])
        return Character.model_validate(data)
