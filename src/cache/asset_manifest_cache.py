from __future__ import annotations

from typing import Any

from src.cache.persistent_cache import PersistentTTLCache


class AssetManifestCache(PersistentTTLCache):
    """Cache for asset manifests with TTL persistence."""

    def __init__(self, ttl_seconds: int = 3600, directory: str | None = None):
        super().__init__("asset_manifest", ttl_seconds=ttl_seconds, directory=directory)

    def get_manifest(self, key: str = "default") -> Any:
        return self.get(key)

    def store_manifest(self, manifest: Any, key: str = "default") -> None:
        self.set(key, manifest)
