from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class PersistentTTLCache:
    """Simple TTL cache that persists to disk.

    Values are stored alongside a timestamp. When a value expires, it is
    removed on the next access and the backing file is rewritten.
    """

    def __init__(self, name: str, ttl_seconds: int = 3600, directory: Path | str | None = None):
        self.ttl_seconds = ttl_seconds
        self.directory = Path(directory) if directory else Path(__file__).resolve().parent
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / f"{name}.json"
        self._store: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text())
            if isinstance(data, dict):
                self._store = data
                self.purge_expired()
        except Exception:
            # Corrupt cache should not crash the application; start fresh.
            self._store = {}

    def _persist(self) -> None:
        try:
            self.path.write_text(json.dumps(self._store))
        except Exception:
            # Avoid raising from persistence failures to keep core flow running.
            pass

    def _is_expired(self, timestamp: float) -> bool:
        return (time.time() - timestamp) > self.ttl_seconds

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return default

        timestamp = entry.get("timestamp", 0)
        if self._is_expired(timestamp):
            self._store.pop(key, None)
            self._persist()
            return default
        return entry.get("value", default)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = {"value": value, "timestamp": time.time()}
        self._persist()

    def purge_expired(self) -> None:
        expired_keys = [k for k, v in self._store.items() if self._is_expired(v.get("timestamp", 0))]
        for key in expired_keys:
            self._store.pop(key, None)
        if expired_keys:
            self._persist()

    def clear(self) -> None:
        self._store.clear()
        try:
            if self.path.exists():
                self.path.unlink()
        except Exception:
            pass
