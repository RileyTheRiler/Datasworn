"""
Database Manager for Starforged AI Game Master.
Handles SQLite connections, schema initialization, and basic CRUD operations
for the persistent world and memory systems.
"""

from __future__ import annotations
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import threading
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseManager")

DB_PATH = "world.db"

SCHEMA_SCRIPT = """
-- Entities (Base table for NPCs, Locations, Factions, Items)
CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,  -- 'npc', 'location', 'faction', 'item'
    name TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    is_active INTEGER DEFAULT 1,
    metadata JSON DEFAULT '{}'
);

-- Aspects (Key-Value facts about entities)
CREATE TABLE IF NOT EXISTS aspects (
    aspect_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL REFERENCES entities(entity_id),
    aspect_key TEXT NOT NULL,
    aspect_value TEXT,
    valid_from INTEGER NOT NULL,
    valid_until INTEGER,  -- NULL = still valid
    source_event_id INTEGER REFERENCES events(event_id),
    UNIQUE(entity_id, aspect_key, valid_from)
);

-- Events (Temporal log of everything that happens)
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,       -- 'observation', 'dialogue', 'action', 'npc_death', etc.
    game_timestamp TEXT NOT NULL,   -- ISO format or game specific
    location_entity_id TEXT REFERENCES entities(entity_id),
    summary TEXT NOT NULL,
    importance INTEGER DEFAULT 5,   -- 1-10
    is_public INTEGER DEFAULT 1,
    embedding BLOB,                 -- For semantic search (stored as bytes/json)
    metadata JSON DEFAULT '{}'      -- Extra data like 'participants', 'tags'
);

-- NPC Knowledge (What each NPC actually knows)
CREATE TABLE IF NOT EXISTS npc_knowledge (
    knowledge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    npc_entity_id TEXT NOT NULL REFERENCES entities(entity_id),
    event_id INTEGER NOT NULL REFERENCES events(event_id),
    learned_at TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,    -- Degrades with rumor chains
    source_type TEXT NOT NULL,      -- 'witnessed', 'told_by', 'rumor', 'public'
    source_entity_id TEXT REFERENCES entities(entity_id),
    UNIQUE(npc_entity_id, event_id)
);

-- Items (Inventory and History)
CREATE TABLE IF NOT EXISTS items (
    item_id TEXT PRIMARY KEY,
    item_type TEXT NOT NULL,
    name TEXT,
    base_description TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT,
    significance_score REAL DEFAULT 0.0,
    current_owner_id TEXT REFERENCES entities(entity_id)
);

-- Item History Events
CREATE TABLE IF NOT EXISTS item_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL REFERENCES items(item_id),
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    actor_id TEXT,
    target_id TEXT,
    description TEXT,
    significance_delta REAL DEFAULT 0.0
);
"""

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        """Initialize database connection and schema."""
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self._create_schema()

    def _create_schema(self):
        """Run schema creation script."""
        try:
            cursor = self.conn.cursor()
            cursor.executescript(SCHEMA_SCRIPT)
            self.conn.commit()
            logger.info("Database schema initialized.")
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")

    def get_connection(self) -> sqlite3.Connection:
        """Get raw connection."""
        return self.conn

    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """Execute a query safely."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor
        except Exception as e:
            logger.error(f"Query failed: {query} with params {params}. Error: {e}")
            raise

    def query(self, query: str, params: Tuple = ()) -> List[dict]:
        """Execute a SELECT query and return list of dicts."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Query failed: {query} | {e}")
            return []

    def close(self):
        """Close connection."""
        if self.conn:
            self.conn.close()

# Singleton accessor
def get_db() -> DatabaseManager:
    return DatabaseManager()
