import time

from src.cache import AssetManifestCache, PromptResultCache
from src.prompting import PromptContext


def test_prompt_cache_persistence(tmp_path):
    cache = PromptResultCache(ttl_seconds=60, directory=tmp_path)
    context = PromptContext(scene_summary="Abandoned station")
    key = cache.make_key("What do we see?", context)
    cache.store_prompt("What do we see?", context, "Echoing halls")

    reloaded = PromptResultCache(ttl_seconds=60, directory=tmp_path)
    assert reloaded.get(key) == "Echoing halls"

    # Force expiration by manipulating timestamp
    reloaded._store[key]["timestamp"] = time.time() - 120
    assert reloaded.get(key) is None


def test_asset_manifest_cache_roundtrip(tmp_path):
    cache = AssetManifestCache(ttl_seconds=1, directory=tmp_path)
    manifest = {"sprites": ["a.png", "b.png"], "version": "1.0"}
    cache.store_manifest(manifest)

    fresh = AssetManifestCache(ttl_seconds=1, directory=tmp_path)
    assert fresh.get_manifest() == manifest

    # Expire and ensure eviction
    for entry in fresh._store.values():
        entry["timestamp"] = time.time() - 5
    assert fresh.get_manifest() is None
