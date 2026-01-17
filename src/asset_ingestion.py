"""Safe helpers for ingesting external asset files."""
from __future__ import annotations

from pathlib import Path

from src.security_utils import sanitize_filename, sanitize_relative_path, validate_payload_size


DEFAULT_MAX_ASSET_BYTES = 5 * 1024 * 1024


def ingest_asset_bytes(base_dir: Path, relative_path: str, payload: bytes, max_bytes: int = DEFAULT_MAX_ASSET_BYTES) -> Path:
    """Persist asset bytes into ``base_dir`` with path safety checks."""
    validate_payload_size(payload, max_bytes)
    path_obj = Path(relative_path)
    if path_obj.is_absolute() or ".." in path_obj.parts:
        raise ValueError("Path traversal detected")

    safe_name = sanitize_filename(path_obj.name)
    safe_path = sanitize_relative_path(base_dir, safe_name)
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    safe_path.write_bytes(payload)
    return safe_path
